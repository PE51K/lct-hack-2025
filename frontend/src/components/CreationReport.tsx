import { Card, Button, Space, Typography, Alert } from 'antd';
import { CheckCircleOutlined, EditOutlined, LinkOutlined } from '@ant-design/icons';
import ConfigViewer from './ConfigViewer';
import { t } from '../i18n';

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