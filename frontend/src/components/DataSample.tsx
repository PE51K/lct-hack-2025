import { Card, Typography, List } from 'antd';

interface DataSampleProps {
  records?: unknown[];
  title?: string;
}

const { Title } = Typography;

const formatRecord = (record: unknown) => {
  try {
    return JSON.stringify(record, null, 2);
  } catch {
    return String(record);
  }
};

const DataSample: React.FC<DataSampleProps> = ({ records, title }) => {
  if (!records || records.length === 0) {
    return null;
  }

  return (
    <Card>
      <Title level={4} style={{ marginBottom: 16 }}>
        {title || 'Семпл данных'}
      </Title>
      <List
        style={{ marginTop: 12 }}
        dataSource={records.slice(0, 1)}
        renderItem={(item) => (
          <List.Item>
            <pre
              style={{
                width: '100%',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                margin: 0,
              }}
            >
              {formatRecord(item)}
            </pre>
          </List.Item>
        )}
      />
    </Card>
  );
};

export default DataSample;
