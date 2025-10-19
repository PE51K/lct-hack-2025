import { useState } from 'react';
import { Card, Form, Input, InputNumber, Button, Space, Typography, message, Divider } from 'antd';
import { DatabaseOutlined, EyeOutlined, HomeOutlined } from '@ant-design/icons';
import DatabaseViewer from './DatabaseViewer';
import { fetchPostgresData, type PostgresColumn } from '../services/api';
import { settingsService } from '../services/settings';

const { Title, Text } = Typography;

interface ViewResultsProps {
  onClose?: () => void;
}

const ViewResults: React.FC<ViewResultsProps> = ({ onClose }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [postgresData, setPostgresData] = useState<{
    columns: PostgresColumn[];
    rows: Record<string, any>[];
    totalRows: number;
    tableName: string;
    schema: string;
  } | null>(null);

  // Load default values from settings
  const defaultValues = () => {
    const savedCreds = settingsService.getPostgresCredentials();
    if (savedCreds) {
      return {
        host: savedCreds.host,
        port: savedCreds.port,
        database: savedCreds.database,
        username: savedCreds.username,
        password: savedCreds.password,
        schema: savedCreds.schema || 'public',
        table: savedCreds.table || '',
      };
    }
    return {
      host: 'test-postgres',
      port: 5432,
      database: 'test_postgres',
      username: 'test_postgres',
      password: 'secure_postgres_password',
      schema: 'public',
      table: '',
    };
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const response = await fetchPostgresData({
        host: values.host,
        port: values.port,
        database: values.database,
        username: values.username,
        password: values.password,
        schema: values.schema || 'public',
        table: values.table,
        limit: 100,
      });

      if (response.success) {
        setPostgresData({
          columns: response.columns,
          rows: response.rows,
          totalRows: response.total_rows,
          tableName: values.table,
          schema: values.schema || 'public',
        });
        message.success('Данные успешно загружены из PostgreSQL!');
      } else {
        message.error(response.error_message || 'Failed to fetch PostgreSQL data');
      }
    } catch (error) {
      console.error('Error fetching PostgreSQL data:', error);
      message.error('Ошибка при получении данных из PostgreSQL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto' }}>
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
              <DatabaseOutlined /> Просмотр результатов ETL
            </Title>
            <Text type="secondary">
              Введите данные для подключения к PostgreSQL, чтобы увидеть результаты загруженных данных
            </Text>
          </div>

          {onClose && (
            <div style={{ textAlign: 'center' }}>
              <Button
                icon={<HomeOutlined />}
                onClick={onClose}
                size="large"
              >
                Вернуться к созданию ETL
              </Button>
            </div>
          )}

          <Divider />

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={defaultValues()}
            size="large"
          >
            <Form.Item
              name="host"
              label="Host"
              rules={[{ required: true, message: 'Пожалуйста, введите host' }]}
            >
              <Input placeholder="test-postgres" />
            </Form.Item>

            <Form.Item
              name="port"
              label="Port"
              rules={[{ required: true, message: 'Пожалуйста, введите port' }]}
            >
              <InputNumber placeholder="5432" style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="database"
              label="Database"
              rules={[{ required: true, message: 'Пожалуйста, введите database' }]}
            >
              <Input placeholder="test_postgres" />
            </Form.Item>

            <Form.Item
              name="username"
              label="Username"
              rules={[{ required: true, message: 'Пожалуйста, введите username' }]}
            >
              <Input placeholder="test_postgres" />
            </Form.Item>

            <Form.Item
              name="password"
              label="Password"
              rules={[{ required: true, message: 'Пожалуйста, введите password' }]}
            >
              <Input.Password placeholder="secure_postgres_password" />
            </Form.Item>

            <Form.Item
              name="schema"
              label="Schema"
            >
              <Input placeholder="public" />
            </Form.Item>

            <Form.Item
              name="table"
              label="Table"
              rules={[{ required: true, message: 'Пожалуйста, введите table name' }]}
              help="Введите название таблицы, данные которой хотите посмотреть"
            >
              <Input placeholder="my_table" />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                block
                icon={<EyeOutlined />}
                loading={loading}
              >
                Показать результаты
              </Button>
            </Form.Item>
          </Form>
        </Space>
      </Card>

      {postgresData && (
        <div style={{ marginTop: 24 }}>
          <DatabaseViewer
            tableName={postgresData.tableName}
            schema={postgresData.schema}
            columns={postgresData.columns}
            rows={postgresData.rows}
            totalRows={postgresData.totalRows}
          />
        </div>
      )}
    </div>
  );
};

export default ViewResults;
