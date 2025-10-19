import { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, Space, Alert, Collapse } from 'antd';
import { RocketOutlined, UserOutlined, ApiOutlined, BulbOutlined, UploadOutlined } from '@ant-design/icons';
import type { CreateETLRequest } from '../services/api';
import { settingsService } from '../services/settings';
import { t } from '../i18n';
import FileUploader from './FileUploader';

const { TextArea } = Input;
const { Title, Paragraph } = Typography;

const generateRandomId = () => Math.random().toString(36).substring(2, 15);

const EXAMPLE_PROMPT = `Connect to S3-compatible storage using endpoint: http://localhost:9002, bucket: test-bucket, access_key: test_minio, secret_key: secure_minio_password and extract data from folder: xml/`;

interface InputFormProps {
  onSubmit: (request: CreateETLRequest) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [form] = Form.useForm();
  const [threadId] = useState(generateRandomId());
  const [userId] = useState(generateRandomId());

  useEffect(() => {
    // Load default prompt from settings
    const defaultPrompt = settingsService.getDefaultPrompt();

    form.setFieldsValue({
      threadId,
      userId,
      userPrompt: defaultPrompt || '',
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

  const handleUseExample = () => {
    form.setFieldsValue({ userPrompt: EXAMPLE_PROMPT });
  };

  const handleFileUploadSuccess = (bucket: string, filePath: string) => {
    // Extract folder from file path
    const folder = filePath.substring(0, filePath.lastIndexOf('/'));

    // Generate prompt with uploaded file details
    const uploadedFilePrompt = `Connect to S3-compatible storage using endpoint: http://test-minio:9002, bucket: ${bucket}, access_key: test_minio, secret_key: secure_minio_password and extract data from folder: ${folder}/`;

    form.setFieldsValue({ userPrompt: uploadedFilePrompt });
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

        <Alert
          message="Тестовый пример"
          description={
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Paragraph style={{ margin: 0 }}>
                Попробуйте создать ETL конфигурацию с тестовыми данными из MinIO
              </Paragraph>
              <Button
                type="link"
                icon={<BulbOutlined />}
                onClick={handleUseExample}
                style={{ padding: 0 }}
              >
                Использовать пример промпта
              </Button>
            </Space>
          }
          type="success"
          showIcon
        />

        <Collapse
          items={[
            {
              key: '1',
              label: (
                <Space>
                  <UploadOutlined />
                  <span>Загрузить свой файл в MinIO</span>
                </Space>
              ),
              children: <FileUploader onUploadSuccess={handleFileUploadSuccess} />,
            },
          ]}
          style={{ marginBottom: 24 }}
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