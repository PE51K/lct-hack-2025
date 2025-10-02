import { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, Space, Alert } from 'antd';
import { RocketOutlined, UserOutlined, ApiOutlined } from '@ant-design/icons';
import type { CreateETLRequest } from '../services/api';
import { t } from '../i18n';

const { TextArea } = Input;
const { Title, Paragraph } = Typography;

const generateRandomId = () => Math.random().toString(36).substring(2, 15);

interface InputFormProps {
  onSubmit: (request: CreateETLRequest) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [form] = Form.useForm();
  const [threadId] = useState(generateRandomId());
  const [userId] = useState(generateRandomId());

  useEffect(() => {
    form.setFieldsValue({
      threadId,
      userId,
    });
  }, [form, threadId, userId]);

  const handleSubmit = (values: { userPrompt: string }) => {
    onSubmit({
      user_prompt: values.userPrompt,
      ids: {
        thread_id: threadId,
        user_id: userId,
      },
    });
  };

  return (
    <Card
      style={{
        maxWidth: 800,
        margin: '0 auto',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={2}>
            <RocketOutlined /> {t('inputForm.title')}
          </Title>
          <Paragraph type="secondary">
            {t('inputForm.description')}
          </Paragraph>
        </div>

        <Alert
          message="AI ассистент"
          description="Опишите ваш источник данных, целевую систему и требования к обработке. AI автоматически создаст оптимальную конфигурацию ETL."
          type="info"
          showIcon
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          size="large"
        >
          <Form.Item
            name="userPrompt"
            label={t('inputForm.userPromptLabel')}
            rules={[{ required: true, message: 'Пожалуйста, опишите задачу' }]}
            help={t('inputForm.userPromptHelp')}
          >
            <TextArea
              rows={6}
              placeholder={t('inputForm.userPromptPlaceholder')}
              style={{ fontSize: '14px' }}
            />
          </Form.Item>

          <Form.Item
            name="threadId"
            label={t('inputForm.threadIdLabel')}
          >
            <Input
              prefix={<ApiOutlined />}
              disabled
              style={{ color: '#666' }}
            />
          </Form.Item>

          <Form.Item
            name="userId"
            label={t('inputForm.userIdLabel')}
          >
            <Input
              prefix={<UserOutlined />}
              disabled
              style={{ color: '#666' }}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              icon={<RocketOutlined />}
            >
              {t('inputForm.submitButton')}
            </Button>
          </Form.Item>
        </Form>
      </Space>
    </Card>
  );
};

export default InputForm;