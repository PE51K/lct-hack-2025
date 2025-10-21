import { useMemo } from 'react';
import { Card, Table, Typography, Space, Alert, Tag, Divider } from 'antd';
import { DatabaseOutlined, TableOutlined, InfoCircleOutlined } from '@ant-design/icons';
import ReactFlow, {
  type Node,
  type Edge,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

const { Text } = Typography;

interface Column {
  name: string;
  type: string;
}

interface DatabaseViewerProps {
  tableName: string;
  schema?: string;
  columns: Column[];
  rows: Record<string, unknown>[];
  totalRows: number;
}

const DatabaseViewer: React.FC<DatabaseViewerProps> = ({
  tableName,
  schema = 'public',
  columns,
  rows,
  totalRows,
}) => {
  // Create nodes and edges for React Flow
  const initialNodes: Node[] = useMemo(() => {
    const tableNode: Node = {
      id: 'table-schema',
      type: 'default',
      data: {
        label: (
          <div style={{ padding: '12px', minWidth: '250px' }}>
            <div style={{
              fontWeight: 'bold',
              fontSize: '16px',
              marginBottom: '12px',
              borderBottom: '2px solid #4A90E2',
              paddingBottom: '8px',
            }}>
              <DatabaseOutlined /> {schema}.{tableName}
            </div>
            <div style={{ fontSize: '12px' }}>
              {columns.map((col, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '4px 0',
                    borderBottom: idx < columns.length - 1 ? '1px solid #e8e8e8' : 'none',
                  }}
                >
                  <Text strong style={{ color: '#4A90E2' }}>{col.name}</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: '11px' }}>{col.type}</Text>
                </div>
              ))}
            </div>
            <Divider style={{ margin: '8px 0' }} />
            <div style={{ fontSize: '11px', color: '#666' }}>
              <InfoCircleOutlined /> {totalRows} rows total
            </div>
          </div>
        ),
      },
      position: { x: 250, y: 100 },
      style: {
        background: '#0B0F14',
        color: '#F5F7FF',
        border: '2px solid #4A90E2',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(74, 144, 226, 0.3)',
      },
    };

    return [tableNode];
  }, [tableName, schema, columns, totalRows]);

  const initialEdges: Edge[] = [];

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  // Create columns for Ant Design Table
  const tableColumns = columns.map((col) => ({
    title: (
      <Space>
        <Text strong>{col.name}</Text>
        <Tag color="blue">{col.type}</Tag>
      </Space>
    ),
    dataIndex: col.name,
    key: col.name,
    render: (value: unknown) => {
      if (value === null || value === undefined) {
        return <Text type="secondary">NULL</Text>;
      }
      return <Text code>{String(value)}</Text>;
    },
  }));

  const dataSource = rows.map((row, idx) => ({ ...row, key: idx }));

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="Результаты загрузки в PostgreSQL"
          description={`Таблица ${schema}.${tableName} успешно создана и заполнена данными. Ниже вы можете увидеть схему таблицы и предпросмотр данных (первые ${rows.length} из ${totalRows} строк).`}
          type="success"
          showIcon
          icon={<DatabaseOutlined />}
        />

        {/* React Flow Graph Visualization */}
        <Card
          title={
            <Space>
              <DatabaseOutlined />
              <span>Схема таблицы</span>
            </Space>
          }
          style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
        >
          <div style={{ height: '400px', background: '#0B0F14', borderRadius: '8px' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              fitView
              attributionPosition="bottom-left"
            >
              <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#1D2B44" />
              <Controls style={{ background: '#1D2B44', border: '1px solid #4A90E2' }} />
            </ReactFlow>
          </div>
        </Card>

        {/* Data Table */}
        <Card
          title={
            <Space>
              <TableOutlined />
              <span>Предпросмотр данных</span>
              <Tag color="green">{rows.length} из {totalRows} строк</Tag>
            </Space>
          }
          style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
        >
          <Table
            columns={tableColumns}
            dataSource={dataSource}
            pagination={{
              pageSize: 10,
              showSizeChanger: false,
              showTotal: (total) => `Всего ${total} строк`,
            }}
            scroll={{ x: 'max-content' }}
            size="small"
          />
        </Card>

        <Alert
          message="Информация"
          description={
            <div>
              <p style={{ margin: 0 }}>
                Данные были успешно загружены в PostgreSQL.
                {totalRows > rows.length && ` Показаны первые ${rows.length} строк из ${totalRows}.`}
              </p>
              <p style={{ marginTop: 8, marginBottom: 0 }}>
                Вы можете подключиться к базе данных напрямую используя PostgreSQL клиент для просмотра всех данных.
              </p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginTop: 16 }}
        />
      </Space>
    </div>
  );
};

export default DatabaseViewer;
