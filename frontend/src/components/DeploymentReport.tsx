import { Card, Result, Button, Timeline, Typography } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  LinkOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { t } from '../i18n';
import DataSampleViewer from './DataSampleViewer';

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
  // Check if we have all required credentials for DataSampleViewer
  const hasValidCredentials =
    dbCredentials &&
    typeof dbCredentials.host === 'string' &&
    typeof dbCredentials.port === 'number' &&
    typeof dbCredentials.database === 'string' &&
    typeof dbCredentials.username === 'string' &&
    typeof dbCredentials.password === 'string' &&
    typeof dbCredentials.table === 'string';

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

      {success && hasValidCredentials && (
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
    </>
  );
};

export default DeploymentReport;