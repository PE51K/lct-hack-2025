"""Airflow DAG file generator."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from models.dag import DAG
from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig

logger = logging.getLogger(__name__)


class AirflowFileGenerator:
    """Generates executable Airflow DAG files from configuration models."""

    def __init__(self, base_output_dir: Path | str = "dags"):
        """
        Initialize the file generator.

        Args:
            base_output_dir: Base directory for generated DAG files (relative to backend/)
        """
        # Resolve path relative to the file_generator.py location
        # This ensures we always write to backend/dags regardless of where the app runs from
        if not Path(base_output_dir).is_absolute():
            # Get the backend directory (3 levels up from this file)
            backend_dir = Path(__file__).parent.parent.parent
            self.base_output_dir = backend_dir / base_output_dir
        else:
            self.base_output_dir = Path(base_output_dir)

        self.base_output_dir.mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False, # noqa: S701
        )

        logger.info(f"AirflowFileGenerator initialized with output dir: {self.base_output_dir}")

    async def generate_dag_files(
        self,
        dag: DAG,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
        user_id: str,
        thread_id: str,
    ) -> dict[str, str]:
        """
        Generate complete set of Airflow files.

        Args:
            dag: DAG configuration model
            extract_config: Extract configuration
            transform_config: Transform configuration
            load_config: Load configuration
            ddl: DDL statements
            user_id: User identifier
            thread_id: Thread identifier

        Returns:
            Dictionary mapping file types to file paths:
            {
                'dag_file': 'path/to/dag.py',
                'functions_file': 'path/to/functions.py',
                'config_file': 'path/to/config.py',
                'init_file': 'path/to/__init__.py'
            }
        """
        logger.info(f"Generating DAG files for user={user_id}, thread={thread_id}")

        # Create user/thread directory structure
        output_dir = self.base_output_dir / user_id / thread_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate DAG ID
        dag_id = f"etl_{user_id}_{thread_id}"

        # Prepare context for templates
        context = self._prepare_template_context(
            dag=dag,
            extract_config=extract_config,
            transform_config=transform_config,
            load_config=load_config,
            ddl=ddl,
            user_id=user_id,
            thread_id=thread_id,
            dag_id=dag_id,
        )

        # Generate files
        generated_files = {}

        try:
            # 1. Main DAG file
            dag_file = output_dir / f"{dag_id}.py"
            dag_content = self._render_template("dag_template.py.j2", context)
            self._write_file(dag_file, dag_content)
            generated_files["dag_file"] = str(dag_file)
            logger.info(f"✅ Generated DAG file: {dag_file}")

            # 2. Functions module
            functions_file = output_dir / f"{dag_id}_functions.py"
            functions_content = self._render_template("functions_template.py.j2", context)
            self._write_file(functions_file, functions_content)
            generated_files["functions_file"] = str(functions_file)
            logger.info(f"✅ Generated functions file: {functions_file}")

            # 3. Config module
            config_file = output_dir / f"{dag_id}_config.py"
            config_content = self._render_template("config_template.py.j2", context)
            self._write_file(config_file, config_content)
            generated_files["config_file"] = str(config_file)
            logger.info(f"✅ Generated config file: {config_file}")

            # 4. __init__.py to make it a package
            init_file = output_dir / "__init__.py"
            self._write_file(init_file, "# Auto-generated package\n")
            generated_files["init_file"] = str(init_file)
            logger.info(f"✅ Generated __init__.py: {init_file}")

            logger.info(f"🎉 Successfully generated {len(generated_files)} files")
            return generated_files

        except Exception as e:
            logger.error(f"❌ Error generating DAG files: {e}", exc_info=True)
            # Clean up partially generated files
            self._cleanup_files(generated_files)
            raise

    def _prepare_template_context(
        self,
        dag: DAG,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
        user_id: str,
        thread_id: str,
        dag_id: str,
    ) -> dict[str, Any]:
        """
        Prepare context dictionary for template rendering.

        Args:
            dag: DAG configuration
            extract_config: Extract configuration
            transform_config: Transform configuration
            load_config: Load configuration
            ddl: DDL statements
            user_id: User identifier
            thread_id: Thread identifier
            dag_id: Generated DAG ID

        Returns:
            Context dictionary for Jinja2 templates
        """
        return {
            # DAG metadata
            "dag_id": dag_id,
            "description": dag.description,
            "created_at": datetime.now().isoformat(),
            "user_id": user_id,
            "thread_id": thread_id,
            # Scheduling
            "schedule": dag.schedule,
            "start_date": dag.start_date,
            "catchup": dag.catchup,
            "max_active_runs": dag.max_active_runs,
            # Ownership
            "owner": dag.owner or "data_team",
            "tags": dag.tags,
            # Default args
            "email_on_failure": dag.default_args.email_on_failure,
            "email_on_retry": dag.default_args.email_on_retry,
            "retries": dag.default_args.retries,
            "retry_delay_minutes": dag.default_args.retry_delay_minutes,
            "execution_timeout_minutes": dag.default_args.execution_timeout_minutes,
            # Tasks
            "tasks": dag.tasks,
            # Resources
            "total_cpu_cores": dag.total_cpu_cores,
            "total_memory_mb": dag.total_memory_mb,
            "estimated_runtime_minutes": dag.estimated_runtime_minutes,
            # Configurations
            "extract_config": extract_config,
            "transform_config": transform_config,
            "load_config": load_config,
            "ddl": ddl,
        }

    def _render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given context.

        Args:
            template_name: Name of the template file
            context: Context dictionary for rendering

        Returns:
            Rendered template content
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise

    def _write_file(self, file_path: Path, content: str) -> None:
        """
        Write content to a file.

        Args:
            file_path: Path to the output file
            content: Content to write
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.debug(f"Wrote file: {file_path}")
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise

    def _cleanup_files(self, generated_files: dict[str, str]) -> None:
        """
        Clean up partially generated files in case of error.

        Args:
            generated_files: Dictionary of generated file paths
        """
        logger.warning("Cleaning up partially generated files")
        for _file_type, file_path in generated_files.items():
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    logger.debug(f"Deleted: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting {file_path}: {e}")

    def delete_dag_files(self, user_id: str, thread_id: str) -> bool:
        """
        Delete all DAG files for a specific user/thread.

        Args:
            user_id: User identifier
            thread_id: Thread identifier

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            dag_dir = self.base_output_dir / user_id / thread_id
            if dag_dir.exists():
                import shutil

                shutil.rmtree(dag_dir)
                logger.info(f"✅ Deleted DAG directory: {dag_dir}")
                return True
            else:
                logger.warning(f"DAG directory not found: {dag_dir}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting DAG files: {e}", exc_info=True)
            return False

    def list_generated_dags(self, user_id: str | None = None) -> list[dict[str, str]]:
        """
        List all generated DAGs, optionally filtered by user.

        Args:
            user_id: Optional user identifier to filter by

        Returns:
            List of DAG information dictionaries
        """
        dags = []

        try:
            if user_id:
                user_dirs = [self.base_output_dir / user_id]
            else:
                user_dirs = [d for d in self.base_output_dir.iterdir() if d.is_dir()]

            for user_dir in user_dirs:
                if not user_dir.is_dir():
                    continue

                user_id_str = user_dir.name
                thread_dirs = [d for d in user_dir.iterdir() if d.is_dir()]

                for thread_dir in thread_dirs:
                    thread_id_str = thread_dir.name
                    dag_id = f"etl_{user_id_str}_{thread_id_str}"
                    dag_file = thread_dir / f"{dag_id}.py"

                    if dag_file.exists():
                        dags.append(
                            {
                                "dag_id": dag_id,
                                "user_id": user_id_str,
                                "thread_id": thread_id_str,
                                "dag_file": str(dag_file),
                                "created_at": datetime.fromtimestamp(
                                    dag_file.stat().st_ctime
                                ).isoformat(),
                            }
                        )

            logger.info(f"Found {len(dags)} generated DAGs")
            return dags

        except Exception as e:
            logger.error(f"Error listing DAGs: {e}", exc_info=True)
            return []
