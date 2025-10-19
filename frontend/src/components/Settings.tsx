import { useState, useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Button, Card, Typography, Space, Alert, Divider, message } from 'antd';
import { SettingOutlined, SaveOutlined, DeleteOutlined, DatabaseOutlined, FileTextOutlined } from '@ant-design/icons';
import { settingsService, type UserSettings } from '../services/settings';

const { Text, Paragraph } = Typography;
const { TextArea } = Input;

interface SettingsProps {
  visible: boolean;
  onClose: () => void;
}

function Settings({ visible, onClose }: SettingsProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible) {
      // Load current settings when modal opens
      const settings = settingsService.getSettings();
      form.setFieldsValue({
        defaultPrompt: settings.defaultPrompt || '',
        postgres_host: settings.postgresCredentials?.host || 'test-postgres',
        postgres_port: settings.postgresCredentials?.port || 5432,
        postgres_database: settings.postgresCredentials?.database || 'test_postgres',
        postgres_username: settings.postgresCredentials?.username || 'test_postgres',
        postgres_password: settings.postgresCredentials?.password || 'secure_postgres_password',
        postgres_schema: settings.postgresCredentials?.schema || 'public',
        postgres_table: settings.postgresCredentials?.table || '',
      });
    }
  }, [visible, form]);

  const handleSave = async (values: any) => {
    setLoading(true);
    try {
      const settings: UserSettings = {
        defaultPrompt: values.defaultPrompt,
        postgresCredentials: {
          host: values.postgres_host,
          port: values.postgres_port,
          database: values.postgres_database,
          username: values.postgres_username,
          password: values.postgres_password,
          schema: values.postgres_schema,
          table: values.postgres_table,
        },
      };

      settingsService.saveSettings(settings);
      message.success('Настройки успешно сохранены');
      onClose();
    } catch (error) {
      message.error('Ошибка при сохранении настроек');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    Modal.confirm({
      title: 'Очистить все настройки?',
      content: 'Это действие нельзя отменить. Все сохранённые данные будут удалены.',
      okText: 'Да, очистить',
      cancelText: 'Отмена',
      okType: 'danger',
      onOk: () => {
        settingsService.clearSettings();
        form.resetFields();
        message.success('Настройки очищены');
      },
    });
  };

  return (
    <Modal
      title={
        <Space>
          <SettingOutlined />
          <span>Настройки</span>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      style={{ top: 20 }}
    >
      <Alert
        message="Автозаполнение форм"
        description="Сохранённые настройки будут автоматически подставляться в формы создания ETL, ускоряя вашу работу."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        size="large"
      >
        {/* Default Prompt Section */}
        <Card
          size="small"
          style={{ marginBottom: 16 }}
          title={
            <Space>
              <FileTextOutlined />
              <Text strong>Промпт по умолчанию</Text>
            </Space>
          }
        >
          <Paragraph type="secondary" style={{ marginBottom: 16 }}>
            Этот промпт будет автоматически подставляться в форму создания ETL
          </Paragraph>
          <Form.Item
            name="defaultPrompt"
            help="Оставьте пустым, чтобы каждый раз вводить вручную"
          >
            <TextArea
              rows={4}
              placeholder="Например: Connect to S3-compatible storage using endpoint: http://localhost:9002..."
            />
          </Form.Item>
        </Card>

        {/* PostgreSQL Credentials Section */}
        <Card
          size="small"
          title={
            <Space>
              <DatabaseOutlined />
              <Text strong>Учётные данные PostgreSQL</Text>
            </Space>
          }
        >
          <Paragraph type="secondary" style={{ marginBottom: 16 }}>
            Эти данные будут автоматически заполняться при создании DAG для PostgreSQL
          </Paragraph>

          <Form.Item
            name="postgres_host"
            label="Хост"
            tooltip="Например: test-postgres (в Docker) или localhost"
          >
            <Input placeholder="test-postgres" />
          </Form.Item>

          <Form.Item
            name="postgres_port"
            label="Порт"
          >
            <InputNumber placeholder="5432" style={{ width: '100%' }} min={1} max={65535} />
          </Form.Item>

          <Form.Item
            name="postgres_database"
            label="База данных"
            tooltip="Внимание: используйте подчёркивание (_), а не дефис (-)"
          >
            <Input placeholder="test_postgres" />
          </Form.Item>

          <Form.Item
            name="postgres_username"
            label="Имя пользователя"
          >
            <Input placeholder="test_postgres" />
          </Form.Item>

          <Form.Item
            name="postgres_password"
            label="Пароль"
          >
            <Input.Password placeholder="secure_postgres_password" />
          </Form.Item>

          <Form.Item
            name="postgres_schema"
            label="Схема"
          >
            <Input placeholder="public" />
          </Form.Item>

          <Form.Item
            name="postgres_table"
            label="Таблица (опционально)"
            help="Можно оставить пустым и указывать каждый раз"
          >
            <Input placeholder="my_table" />
          </Form.Item>
        </Card>

        <Divider />

        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={handleClear}
          >
            Очистить всё
          </Button>
          <Space>
            <Button onClick={onClose}>
              Отмена
            </Button>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={loading}
            >
              Сохранить настройки
            </Button>
          </Space>
        </Space>
      </Form>
    </Modal>
  );
}

export default Settings;
