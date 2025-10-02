import { Card, Timeline, Typography, Tag, Spin, Alert } from 'antd';
import {
  CloudUploadOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { t } from '../i18n';

const { Title, Text } = Typography;

interface DeploymentProgressProps {
  messages: string[];
  isComplete: boolean;
  success?: boolean;
}

const DeploymentProgress: React.FC<DeploymentProgressProps> = ({ messages, isComplete, success }) => {
  return (
    <Card
      style={{
        maxWidth: 800,
        margin: '20px auto',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Title level={4}>
        <CloudUploadOutlined /> {t('deploymentProgress.title')}
      </Title>

      {isComplete && (
        <Alert
          message={success ? t('deploymentProgress.complete') : 'Ошибка публикации'}
          type={success ? 'success' : 'error'}
          showIcon
          style={{ marginBottom: 20 }}
        />
      )}

      <Timeline
        items={messages.map((msg, index) => ({
          key: index,
          dot: isComplete ? (
            success ? (
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
            ) : (
              <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
            )
          ) : index === messages.length - 1 ? (
            <LoadingOutlined />
          ) : (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          ),
          color: isComplete ? (success ? 'green' : 'red') : index === messages.length - 1 ? 'blue' : 'green',
          children: (
            <Text>
              {msg}
              {!isComplete && index === messages.length - 1 && (
                <Tag color="processing" style={{ marginLeft: 8 }}>
                  <Spin size="small" /> В процессе
                </Tag>
              )}
            </Text>
          ),
        }))}
      />
    </Card>
  );
};

export default DeploymentProgress;