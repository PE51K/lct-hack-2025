import { useState } from 'react';
import { Card, Table, Button, Alert, Space, Typography, Spin } from 'antd';
import { TableOutlined, ReloadOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { fetchSample, type FetchSampleRequest } from '../services/api';

const { Text, Paragraph } = Typography;

interface DataSampleViewerProps {
  credentials: {
    host: string;
    port: number;
    database: string;
    username: string;
    password: string;
    schema?: string;
    table: string;
  };
}

function DataSampleViewer({ credentials }: DataSampleViewerProps) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<{
    columns: string[];
    rows: Record<string, unknown>[];
    totalRows: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFetchSample = async () => {
    setLoading(true);
    setError(null);

    try {
      const request: FetchSampleRequest = {
        host: credentials.host,
        port: credentials.port,
        database: credentials.database,
        username: credentials.username,
        password: credentials.password,
        schema: credentials.schema || 'public',
        table: credentials.table,
        limit: 10,
      };

      const response = await fetchSample(request);

      if (response.success) {
        setData({
          columns: response.columns,
          rows: response.rows,
          totalRows: response.total_rows,
        });
      } else {
        setError(response.error_message || 'Неизвестная ошибка при загрузке данных');
      }
    } catch (err) {
      console.error('Error fetching sample:', err);
      setError('Не удалось загрузить образец данных. Проверьте, что DAG успешно выполнился.');
    } finally {
      setLoading(false);
    }
  };

  const tableColumns = data?.columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
    render: (value: unknown) => {
      if (value === null || value === undefined) {
        return <Text type="secondary" italic>null</Text>;
      }
      return <Text>{String(value)}</Text>;
    },
  }));

  return (
    <Card
      style={{
        marginTop: 24,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
      title={
        <Space>
          <TableOutlined />
          <span>Образец загруженных данных</span>
        </Space>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="Просмотр данных"
          description={
            <Paragraph style={{ margin: 0 }}>
              После успешного выполнения DAG в Airflow вы можете просмотреть образец данных, которые были загружены в базу данных.
              Нажмите кнопку ниже, чтобы загрузить первые 10 строк из таблицы <Text code>{credentials.table}</Text>.
            </Paragraph>
          }
          type="info"
          showIcon
        />

        {!data && !error && (
          <Button
            type="primary"
            icon={<TableOutlined />}
            onClick={handleFetchSample}
            loading={loading}
            size="large"
            style={{ width: '100%' }}
          >
            {loading ? 'Загрузка данных...' : 'Загрузить образец данных'}
          </Button>
        )}

        {loading && (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <Paragraph style={{ marginTop: 16 }}>
              Подключение к базе данных и загрузка образца...
            </Paragraph>
          </div>
        )}

        {error && (
          <Alert
            message="Ошибка загрузки данных"
            description={
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Paragraph style={{ margin: 0 }}>{error}</Paragraph>
                <Paragraph type="secondary" style={{ margin: 0 }}>
                  Возможные причины:
                  <ul style={{ marginTop: 8 }}>
                    <li>DAG ещё не выполнился в Airflow (дождитесь завершения)</li>
                    <li>Таблица не была создана (проверьте логи в Airflow)</li>
                    <li>Неверные учётные данные для подключения к БД</li>
                  </ul>
                </Paragraph>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleFetchSample}
                  style={{ marginTop: 8 }}
                >
                  Попробовать снова
                </Button>
              </Space>
            }
            type="error"
            showIcon
          />
        )}

        {data && (
          <>
            <Alert
              message={
                <Space>
                  <CheckCircleOutlined />
                  <span>
                    Успешно загружено {data.rows.length} из {data.totalRows} строк
                  </span>
                </Space>
              }
              type="success"
              showIcon
              action={
                <Button
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={handleFetchSample}
                >
                  Обновить
                </Button>
              }
            />

            <div style={{ overflowX: 'auto' }}>
              <Table
                columns={tableColumns}
                dataSource={data.rows.map((row, index) => ({
                  ...row,
                  key: index,
                }))}
                pagination={false}
                size="small"
                bordered
                style={{ marginTop: 16 }}
                scroll={{ x: true }}
              />
            </div>

            {data.totalRows > 10 && (
              <Alert
                message={`В таблице всего ${data.totalRows} строк. Показаны первые 10.`}
                type="info"
                showIcon
              />
            )}
          </>
        )}
      </Space>
    </Card>
  );
}

export default DataSampleViewer;
