import { useState, useEffect } from 'react';
import { Form, Input, InputNumber, Button, Card, Typography, Space, Alert, Divider, Checkbox } from 'antd';
import { DatabaseOutlined, CheckCircleOutlined, CloseCircleOutlined, RobotOutlined, SaveOutlined } from '@ant-design/icons';
import type { CredentialsRequired } from '../services/api';
import { settingsService } from '../services/settings';
import { t, tReplace } from '../i18n';

const { Title, Text } = Typography;

interface CredentialsFormProps {
  credentialsRequired: CredentialsRequired;
  onSubmit: (credentials: Record<string, unknown>) => void;
  onCancel: () => void;
}

function CredentialsForm({ credentialsRequired, onSubmit, onCancel }: CredentialsFormProps) {
  const [form] = Form.useForm();
  const [saveCredentials, setSaveCredentials] = useState<boolean>(true); // По умолчанию включено
  const [credentials, setCredentials] = useState<Record<string, unknown>>(() => {
    const initial: Record<string, unknown> = {};

    // Auto-fill PostgreSQL credentials from settings if available
    if (credentialsRequired.target_type === 'postgres') {
      const savedCreds = settingsService.getPostgresCredentials();
      if (savedCreds) {
        // Map saved credentials to field names
        const fieldMapping: Record<string, string | number> = {
          'host': savedCreds.host || '',
          'port': savedCreds.port || 5432,
          'database': savedCreds.database || '',
          'username': savedCreds.username || '',
          'password': savedCreds.password || '',
          'schema': savedCreds.schema || 'public',
          'table': savedCreds.table || '',
        };

        credentialsRequired.fields.forEach(field => {
          const mappedValue = fieldMapping[field.name.toLowerCase()];
          if (mappedValue !== undefined && mappedValue !== '') {
            initial[field.name] = mappedValue;
          } else if (field.default !== undefined) {
            initial[field.name] = field.default;
          }
        });
      }
    } else {
      // Use defaults from API for non-postgres targets
      credentialsRequired.fields.forEach(field => {
        if (field.default !== undefined) {
          initial[field.name] = field.default;
        }
      });
    }

    return initial;
  });

  useEffect(() => {
    // Update form values when credentials change
    form.setFieldsValue(credentials);
  }, [form, credentials]);

  const handleSubmit = () => {
    // Сохранить credentials в settings, если пользователь выбрал эту опцию и это PostgreSQL
    if (saveCredentials && credentialsRequired.target_type === 'postgres') {
      const settings = settingsService.getSettings();
      settings.postgresCredentials = {
        host: credentials.host as string,
        port: credentials.port as number,
        database: credentials.database as string,
        username: credentials.username as string,
        password: credentials.password as string,
        schema: credentials.schema as string || 'public',
        table: credentials.table as string || '',
      };
      settingsService.saveSettings(settings);
    }

    onSubmit(credentials);
  };

  const handleValuesChange = (changedValues: Record<string, unknown>) => {
    setCredentials(prev => ({ ...prev, ...changedValues }));
  };

  return (
    <Card
      style={{
        maxWidth: 700,
        margin: '0 auto',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={2}>
            <DatabaseOutlined /> {t('credentialsForm.title')}
          </Title>
        </div>

        <Alert
          message={
            <span>
              <RobotOutlined /> {t('credentialsForm.aiRecommendation')}
            </span>
          }
          description={tReplace('credentialsForm.description', {
            targetType: credentialsRequired.target_type,
          })}
          type="success"
          showIcon
        />

        <Divider />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={handleValuesChange}
          initialValues={credentials}
          size="large"
        >
          {credentialsRequired.fields.map(field => (
            <Form.Item
              key={field.name}
              name={field.name}
              label={
                <span>
                  {field.label}
                  {field.required && (
                    <Text type="danger"> ({t('credentialsForm.required')})</Text>
                  )}
                </span>
              }
              rules={[
                {
                  required: field.required,
                  message: `Пожалуйста, введите ${field.label.toLowerCase()}`,
                },
              ]}
            >
              {field.type === 'number' ? (
                <InputNumber
                  placeholder={field.placeholder}
                  style={{ width: '100%' }}
                />
              ) : field.type === 'password' ? (
                <Input.Password
                  placeholder={field.placeholder}
                  autoComplete="new-password"
                />
              ) : (
                <Input
                  type={field.type}
                  placeholder={field.placeholder}
                />
              )}
            </Form.Item>
          ))}

          {credentialsRequired.target_type === 'postgres' && (
            <Form.Item style={{ marginTop: 24 }}>
              <Checkbox
                checked={saveCredentials}
                onChange={(e) => setSaveCredentials(e.target.checked)}
              >
                <Space>
                  <SaveOutlined />
                  <span>Сохранить эти учётные данные в настройках для последующего использования</span>
                </Space>
              </Checkbox>
            </Form.Item>
          )}

          <Space style={{ width: '100%', marginTop: 20 }} size="middle">
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              icon={<CheckCircleOutlined />}
              style={{ flex: 1 }}
              block
            >
              {t('credentialsForm.submitButton')}
            </Button>
            <Button
              danger
              size="large"
              icon={<CloseCircleOutlined />}
              onClick={onCancel}
              style={{ flex: 1 }}
              block
            >
              {t('credentialsForm.cancelButton')}
            </Button>
          </Space>
        </Form>
      </Space>
    </Card>
  );
}

export default CredentialsForm;