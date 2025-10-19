import { Card, Timeline, Typography, Tag, Spin } from 'antd';
import { SyncOutlined, CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { t } from '../i18n';

const { Title, Text } = Typography;

interface ProgressBarProps {
  messages: string[];
  isComplete: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ messages, isComplete }) => {
  return (
    <Card
      style={{
        maxWidth: 800,
        margin: '20px auto',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Title level={4}>
        {isComplete ? (
          <>
            <CheckCircleOutlined style={{ color: '#52c41a' }} /> Завершено
          </>
        ) : (
          <>
            <SyncOutlined spin /> {t('progressBar.generating')}
          </>
        )}
      </Title>

      <Timeline
        items={messages.map((msg, index) => ({
          key: index,
          dot: index === messages.length - 1 && !isComplete ? (
            <LoadingOutlined />
          ) : (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          ),
          color: index === messages.length - 1 && !isComplete ? 'blue' : 'green',
          children: (
            <Text>
              {msg}
              {index === messages.length - 1 && !isComplete && (
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

export default ProgressBar;