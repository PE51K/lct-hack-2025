import { useState, useEffect, useRef, useCallback } from 'react';
import { Form, Input, Button, Card, Typography, Space, Alert, Upload, message } from 'antd';
import type { UploadProps } from 'antd';
import { RocketOutlined, UserOutlined, ApiOutlined, BulbOutlined, UploadOutlined } from '@ant-design/icons';
import type { CreateETLRequest, UploadSourceResponse } from '../services/api';
import { uploadSourceFile } from '../services/api';
import { t } from '../i18n';
import DataSample from './DataSample';

const { TextArea } = Input;
const { Title, Paragraph } = Typography;

const generateRandomId = () => Math.random().toString(36).substring(2, 15);

const EXAMPLE_PROMPT = `Connect to S3-compatible storage using endpoint: http://localhost:9000, bucket: test-bucket, access_key: test_minio, secret_key: secure_minio_password and extract data from folder: xml/`;

interface InputFormProps {
  onSubmit: (request: CreateETLRequest) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [form] = Form.useForm();
  const [threadId] = useState(generateRandomId());
  const [userId] = useState(generateRandomId());
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadSourceResponse | null>(null);
  const autoSubmitTriggeredRef = useRef(false);

  useEffect(() => {
    form.setFieldsValue({
      threadId,
      userId,
    });
  }, [form, threadId, userId]);

  const handleSubmit = useCallback((values: { userPrompt: string }) => {
    onSubmit({
      user_prompt: values.userPrompt,
      ids: {
        thread_id: threadId,
        user_id: userId,
      },
      uploaded_source_uri: uploadResult?.source_uri,
    });
  }, [onSubmit, threadId, userId, uploadResult]);

  const handleUseExample = () => {
    form.setFieldsValue({ userPrompt: EXAMPLE_PROMPT });
  };

  const uploadProps: UploadProps = {
    maxCount: 1,
    accept: '.xml,.csv,.json',
    showUploadList: false,
    beforeUpload: file => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (!extension || !['xml', 'csv', 'json'].includes(extension)) {
        message.error('Поддерживаются только файлы с расширениями xml, csv или json.');
        return Upload.LIST_IGNORE;
      }
      return true;
    },
    customRequest: async options => {
      const { file, onError, onSuccess } = options;
      setUploading(true);
      setUploadResult(null);
      autoSubmitTriggeredRef.current = false;
      try {
        const result = await uploadSourceFile(file as File, {
          thread_id: threadId,
          user_id: userId,
        });
        setUploadResult(result);
        message.success(`Файл ${result.filename} успешно загружен и проанализирован.`);
        onSuccess?.(result);
      } catch (error) {
        console.error('File upload failed:', error);
        setUploadResult(null);
        message.error('Не удалось загрузить файл. Попробуйте снова.');
        onError?.(error as Error);
      } finally {
        setUploading(false);
      }
    },
  };

  useEffect(() => {
    if (!uploadResult || autoSubmitTriggeredRef.current) {
      return;
    }

    const currentPrompt: string | undefined = form.getFieldValue('userPrompt');
    let promptToUse = currentPrompt?.trim();

    if (!promptToUse) {
      promptToUse = `Создай ETL конвейер для локального файла ${uploadResult.filename} (формат ${uploadResult.content_type || 'неизвестен'}), используй сохранённый источник ${uploadResult.source_uri}.`;
      form.setFieldsValue({ userPrompt: promptToUse });
    }

    autoSubmitTriggeredRef.current = true;
    handleSubmit({ userPrompt: promptToUse });
  }, [form, handleSubmit, uploadResult]);

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

        <Card type="inner" title="Загрузка файла источника">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph style={{ marginBottom: 0 }}>
              Загрузите файл в формате XML, CSV или JSON — мы сохраним его и построим extract-конфигурацию локально.
            </Paragraph>
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />} loading={uploading}>
                Загрузить файл
              </Button>
            </Upload>
            {uploadResult ? (
              <Alert
                type="success"
                showIcon
                message={`Файл ${uploadResult.filename} обработан`}
                description={
                  <Space direction="vertical">
                    <span>Определён тип контента: {uploadResult.content_type || 'неизвестно'}</span>
                    <span>
                      Путь хранения: <Typography.Text code>{uploadResult.stored_path}</Typography.Text>
                    </span>
                    <span>
                      Путь для Airflow: <Typography.Text code>{uploadResult.container_source_uri}</Typography.Text>
                    </span>
                  </Space>
                }
              />
            ) : null}

            <DataSample
              records={(uploadResult?.extract_config as Record<string, unknown> | undefined)?.sample_records as unknown[] | undefined}
              title="Семпл данных"
            />
          </Space>
        </Card>

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
