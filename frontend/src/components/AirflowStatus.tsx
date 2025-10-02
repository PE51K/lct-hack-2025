import { Card, Tag, Typography, Descriptions, Button, Space } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  ClockCircleOutlined,
  LinkOutlined,
} from '@ant-design/icons';
import { t } from '../i18n';

const { Title, Text } = Typography;

interface AirflowStatusProps {
  dagId?: string;
  airflowUrl?: string;
  status?: 'success' | 'failed' | 'running' | 'queued';
  lastRun?: string;
  nextRun?: string;
}

const AirflowStatus: React.FC<AirflowStatusProps> = ({
  dagId,
  airflowUrl,
  status,
  lastRun,
  nextRun,
}) => {
  const getStatusTag = () => {
    switch (status) {
      case 'success':
        return <Tag icon={<CheckCircleOutlined />} color="success">{t('airflowStatus.success')}</Tag>;
      case 'failed':
        return <Tag icon={<CloseCircleOutlined />} color="error">{t('airflowStatus.failed')}</Tag>;
      case 'running':
        return <Tag icon={<SyncOutlined spin />} color="processing">{t('airflowStatus.running')}</Tag>;
      case 'queued':
        return <Tag icon={<ClockCircleOutlined />} color="default">{t('airflowStatus.queued')}</Tag>;
      default:
        return <Tag color="default">Неизвестно</Tag>;
    }
  };

  if (!dagId) {
    return null;
  }

  return (
    <Card
      style={{
        maxWidth: 800,
        margin: '20px auto',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Title level={4}>
          <SyncOutlined /> {t('airflowStatus.title')}
        </Title>

        <Descriptions bordered column={1}>
          <Descriptions.Item label={t('airflowStatus.dagId')}>
            <Text code>{dagId}</Text>
          </Descriptions.Item>
          {status && (
            <Descriptions.Item label={t('airflowStatus.status')}>
              {getStatusTag()}
            </Descriptions.Item>
          )}
          {lastRun && (
            <Descriptions.Item label={t('airflowStatus.lastRun')}>
              {lastRun}
            </Descriptions.Item>
          )}
          {nextRun && (
            <Descriptions.Item label={t('airflowStatus.nextRun')}>
              {nextRun}
            </Descriptions.Item>
          )}
        </Descriptions>

        {airflowUrl && (
          <Button
            type="primary"
            icon={<LinkOutlined />}
            href={airflowUrl}
            target="_blank"
            size="large"
          >
            {t('airflowStatus.viewInAirflow')}
          </Button>
        )}
      </Space>
    </Card>
  );
};

export default AirflowStatus;
