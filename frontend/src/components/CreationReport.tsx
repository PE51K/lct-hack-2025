import { useState } from 'react';
import { Card, Button, Space, Typography, Alert, message } from 'antd';
import { CheckCircleOutlined, EditOutlined, ThunderboltOutlined, LinkOutlined } from '@ant-design/icons';
import ConfigViewer from './ConfigViewer';
import { t } from '../i18n';
import { triggerDAG } from '../services/api';

const { Title } = Typography;

interface CreationReportProps {
  extractConfig?: Record<string, unknown>;
  transformConfig?: Record<string, unknown>;
  loadConfig?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
  dagId?: string;
  airflowUrl?: string;
  onSatisfied: () => void;
  onNotSatisfied: () => void;
}

const CreationReport: React.FC<CreationReportProps> = ({
  extractConfig,
  transformConfig,
  loadConfig,
  ddl,
  dag,
  dagId,
  airflowUrl,
  onSatisfied,
  onNotSatisfied,
}) => {
  console.log('[CreationReport] Rendered with dagId:', dagId, 'airflowUrl:', airflowUrl);

  const [triggeringDAG, setTriggeringDAG] = useState(false);
  const [dagTriggered, setDagTriggered] = useState(false);

  const handleTriggerDAG = async () => {
    console.log('[CreationReport] Trigger DAG clicked, dagId:', dagId);

    if (!dagId) {
      console.error('[CreationReport] DAG ID is missing!');
      message.error('DAG ID отсутствует');
      return;
    }

    setTriggeringDAG(true);
    try {
      console.log('[CreationReport] Calling triggerDAG API with:', { dag_id: dagId });
      const response = await triggerDAG({ dag_id: dagId });
      console.log('[CreationReport] triggerDAG response:', response);

      if (response.success) {
        setDagTriggered(true);
        message.success(`DAG успешно запущен! Run ID: ${response.dag_run_id || 'unknown'}`);
      } else {
        console.error('[CreationReport] triggerDAG failed:', response.error_message);
        message.error(response.error_message || 'Не удалось запустить DAG');
      }
    } catch (error) {
      console.error('[CreationReport] Error triggering DAG:', error);
      message.error('Ошибка при запуске DAG');
    } finally {
      setTriggeringDAG(false);
    }
  };
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <Card
        style={{
          marginBottom: 24,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>{t('creationReport.title')}</Title>
          </div>

          <Alert
            message={t('creationReport.summary')}
            description="AI ассистент сгенерировал конфигурацию ETL на основе ваших требований. Проверьте настройки ниже и утвердите конфигурацию или запросите изменения."
            type="info"
            showIcon
          />

          <ConfigViewer
            extractConfig={extractConfig}
            transformConfig={transformConfig}
            loadConfig={loadConfig}
            ddl={ddl}
            dag={dag}
          />

          {dagId && (
            <Alert
              message="DAG создан в Airflow"
              description={`DAG ID: ${dagId}. Вы можете запустить DAG сейчас или утвердить конфигурацию для дальнейших действий.`}
              type="success"
              showIcon
            />
          )}

          <Space
            style={{
              width: '100%',
              justifyContent: 'center',
              marginTop: 24,
            }}
            size="large"
            wrap
          >
            {dagId && !dagTriggered && (
              <Button
                type="primary"
                size="large"
                icon={<ThunderboltOutlined />}
                onClick={handleTriggerDAG}
                loading={triggeringDAG}
                style={{ background: '#ffa940', borderColor: '#ffa940' }}
              >
                Запустить DAG
              </Button>
            )}
            {dagTriggered && (
              <Alert
                message="DAG запущен!"
                description="DAG успешно запущен в Airflow. Можете отслеживать выполнение в Airflow UI."
                type="success"
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}
            {airflowUrl && (
              <Button
                size="large"
                icon={<LinkOutlined />}
                href={airflowUrl}
                target="_blank"
              >
                Открыть в Airflow
              </Button>
            )}
            <Button
              type="primary"
              size="large"
              icon={<CheckCircleOutlined />}
              onClick={onSatisfied}
            >
              {t('creationReport.satisfiedButton')}
            </Button>
            <Button
              size="large"
              icon={<EditOutlined />}
              onClick={onNotSatisfied}
            >
              {t('creationReport.notSatisfiedButton')}
            </Button>
          </Space>
        </Space>
      </Card>
    </div>
  );
};

export default CreationReport;