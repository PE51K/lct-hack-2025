import { Card, Timeline, Typography, Tag, Space, Empty } from 'antd';
import {
  RobotOutlined,
  UserOutlined,
  ToolOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { t } from '../i18n';

const { Title, Text, Paragraph } = Typography;

export interface AssistantMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  timestamp?: string;
  toolName?: string;
}

interface AssistantLogProps {
  messages: AssistantMessage[];
}

const AssistantLog: React.FC<AssistantLogProps> = ({ messages }) => {
  const getIcon = (role: string) => {
    switch (role) {
      case 'user':
        return <UserOutlined style={{ fontSize: 16 }} />;
      case 'assistant':
        return <RobotOutlined style={{ fontSize: 16 }} />;
      case 'tool':
        return <ToolOutlined style={{ fontSize: 16 }} />;
      case 'system':
        return <ThunderboltOutlined style={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const getColor = (role: string) => {
    switch (role) {
      case 'user':
        return 'blue';
      case 'assistant':
        return 'green';
      case 'tool':
        return 'orange';
      case 'system':
        return 'purple';
      default:
        return 'default';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'user':
        return t('assistant.userMessage');
      case 'assistant':
        return t('assistant.assistantMessage');
      case 'tool':
        return 'Инструмент';
      case 'system':
        return t('assistant.systemMessage');
      default:
        return role;
    }
  };

  if (!messages || messages.length === 0) {
    return (
      <Card
        style={{
          maxWidth: 1000,
          margin: '20px auto',
        }}
      >
        <Empty description="Нет сообщений от ассистента" />
      </Card>
    );
  }

  return (
    <Card
      style={{
        maxWidth: 1000,
        margin: '20px auto',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Title level={4}>
        <RobotOutlined /> {t('assistant.title')}
      </Title>

      <Timeline
        style={{ marginTop: 24 }}
        items={messages.map((msg, index) => ({
          key: index,
          dot: getIcon(msg.role),
          color: getColor(msg.role),
          children: (
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Space>
                <Tag color={getColor(msg.role)}>{getRoleLabel(msg.role)}</Tag>
                {msg.toolName && (
                  <Tag icon={<ToolOutlined />}>{msg.toolName}</Tag>
                )}
                {msg.timestamp && (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {msg.timestamp}
                  </Text>
                )}
              </Space>
              <Paragraph
                style={{
                  background: msg.role === 'assistant' ? '#f0f9ff' : '#f5f5f5',
                  padding: 12,
                  borderRadius: 4,
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {msg.content}
              </Paragraph>
            </Space>
          ),
        }))}
      />
    </Card>
  );
};

export default AssistantLog;
