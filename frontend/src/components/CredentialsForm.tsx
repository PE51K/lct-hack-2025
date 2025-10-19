import { useState } from 'react';
import { Form, Input, InputNumber, Button, Card, Typography, Space, Alert, Divider } from 'antd';
import { DatabaseOutlined, CheckCircleOutlined, CloseCircleOutlined, RobotOutlined } from '@ant-design/icons';
import type { CredentialsRequired } from '../services/api';
import { t, tReplace } from '../i18n';
import DataSample from './DataSample';

const { Title, Text } = Typography;

interface CredentialsFormProps {
  credentialsRequired: CredentialsRequired;
  onSubmit: (credentials: Record<string, unknown>) => void;
  onCancel: () => void;
  dataSample?: unknown[];
}

function CredentialsForm({ credentialsRequired, onSubmit, onCancel, dataSample }: CredentialsFormProps) {
  const [form] = Form.useForm();
  const [credentials, setCredentials] = useState<Record<string, unknown>>(() => {
    const initial: Record<string, unknown> = {};
    credentialsRequired.fields.forEach(field => {
      if (field.default !== undefined) {
        initial[field.name] = field.default;
      }
    });
    return initial;
  });

  const handleSubmit = () => {
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

        <DataSample records={dataSample} title="Семпл данных" />

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
