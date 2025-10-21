import { useState } from 'react';
import { Card, Result, Button, Timeline, Typography, message } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  LinkOutlined,
  ReloadOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { t } from '../i18n';
import DataSampleViewer from './DataSampleViewer';
import DatabaseViewer from './DatabaseViewer';
import { fetchPostgresData, type PostgresColumn } from '../services/api';

const { Text } = Typography;

interface DeploymentReportProps {
  success: boolean;
  messages: string[];
  dagId?: string;
  airflowUrl?: string;
  onCreateNew?: () => void;
  dbCredentials?: Record<string, unknown> | null;
}

const DeploymentReport: React.FC<DeploymentReportProps> = ({
  success,
  messages,
  dagId,
  airflowUrl,
  onCreateNew,
  dbCredentials,
}) => {
  console.log('[DeploymentReport] Rendered with dagId:', dagId, 'airflowUrl:', airflowUrl, 'success:', success);

  const [showDatabaseViewer, setShowDatabaseViewer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dagTriggered, setDagTriggered] = useState(false);
  const [postgresData, setPostgresData] = useState<{
    columns: PostgresColumn[];
    rows: Record<string, unknown>[];
    totalRows: number;
  } | null>(null);

  // Check if we have all required credentials for DataSampleViewer
  const hasValidCredentials =
    dbCredentials &&
    typeof dbCredentials.host === 'string' &&
    typeof dbCredentials.port === 'number' &&
    typeof dbCredentials.database === 'string' &&
    typeof dbCredentials.username === 'string' &&
    typeof dbCredentials.password === 'string' &&
    typeof dbCredentials.table === 'string';

  const handleTriggerDAG = () => {
    console.log('[DeploymentReport] Opening Airflow UI for DAG:', dagId);

    if (!airflowUrl) {
      message.error('Airflow URL отсутствует');
      return;
    }

    // Open Airflow UI in new window
    window.open(airflowUrl, '_blank');

    // Show success message with instructions
    message.info({
      content: (
        <div>
          <div style={{ marginBottom: 8 }}>Airflow UI открыт в новой вкладке.</div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            1. Авторизуйтесь (admin / secure_admin_password)<br/>
            2. Нажмите кнопку ▶ "Trigger DAG"
          </div>
        </div>
      ),
      duration: 10,
    });

    setDagTriggered(true);
  };

  const handleShowResults = async () => {
    if (!hasValidCredentials) {
      message.error('Missing database credentials');
      return;
    }

    setLoading(true);
    try {
      const response = await fetchPostgresData({
        host: dbCredentials.host as string,
        port: dbCredentials.port as number,
        database: dbCredentials.database as string,
        username: dbCredentials.username as string,
        password: dbCredentials.password as string,
        schema: (dbCredentials.schema as string) || 'public',
        table: dbCredentials.table as string,
        limit: 100,
      });

      if (response.success) {
        setPostgresData({
          columns: response.columns,
          rows: response.rows,
          totalRows: response.total_rows,
        });
        setShowDatabaseViewer(true);
        message.success('Данные успешно загружены из PostgreSQL!');
      } else {
        message.error(response.error_message || 'Failed to fetch PostgreSQL data');
      }
    } catch (error) {
      console.error('Error fetching PostgreSQL data:', error);
      message.error('Ошибка при получении данных из PostgreSQL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Card
        style={{
          maxWidth: 900,
          margin: '20px auto',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <Result
          status={success ? 'success' : 'error'}
          title={success ? t('deploymentReport.success') : 'Ошибка при публикации DAG'}
          subTitle={
            success && dagId ? (
              <>
                {t('deploymentReport.dagId')}: <Text code>{dagId}</Text>
              </>
            ) : null
          }
          extra={[
            success && dagId && !dagTriggered && (
              <Button
                key="trigger"
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={handleTriggerDAG}
                size="large"
                style={{ background: '#ffa940', borderColor: '#ffa940' }}
              >
                Запустить DAG
              </Button>
            ),
            success && airflowUrl && (
              <Button
                type="primary"
                key="airflow"
                icon={<LinkOutlined />}
                href={airflowUrl}
                target="_blank"
                size="large"
              >
                {t('deploymentReport.openInAirflow')}
              </Button>
            ),
            success && hasValidCredentials && !showDatabaseViewer && dagTriggered && (
              <Button
                key="show-results"
                type="primary"
                icon={<DatabaseOutlined />}
                onClick={handleShowResults}
                loading={loading}
                size="large"
                style={{ background: '#52c41a', borderColor: '#52c41a' }}
              >
                Показать результаты в PostgreSQL
              </Button>
            ),
            onCreateNew && (
              <Button
                key="new"
                icon={<ReloadOutlined />}
                onClick={onCreateNew}
                size="large"
              >
                {t('deploymentReport.createNew')}
              </Button>
            ),
          ].filter(Boolean)}
        />

        {messages.length > 0 && (
          <>
            <Typography.Title level={5} style={{ marginTop: 24 }}>
              Детали процесса:
            </Typography.Title>
            <Timeline
              items={messages.map((msg, index) => ({
                key: index,
                dot: success ? (
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                ) : (
                  <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                ),
                color: success ? 'green' : 'red',
                children: <Text>{msg}</Text>,
              }))}
            />
          </>
        )}
      </Card>

      {success && hasValidCredentials && !showDatabaseViewer && (
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <DataSampleViewer
            credentials={{
              host: dbCredentials.host as string,
              port: dbCredentials.port as number,
              database: dbCredentials.database as string,
              username: dbCredentials.username as string,
              password: dbCredentials.password as string,
              schema: (dbCredentials.schema as string) || 'public',
              table: dbCredentials.table as string,
            }}
          />
        </div>
      )}

      {showDatabaseViewer && postgresData && hasValidCredentials && (
        <div style={{ marginTop: 24 }}>
          <DatabaseViewer
            tableName={dbCredentials.table as string}
            schema={(dbCredentials.schema as string) || 'public'}
            columns={postgresData.columns}
            rows={postgresData.rows}
            totalRows={postgresData.totalRows}
          />
        </div>
      )}
    </>
  );
};

export default DeploymentReport;
