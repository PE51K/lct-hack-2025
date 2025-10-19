import { Card, Descriptions, Tabs, Typography, Tag, Space, Collapse } from 'antd';
import {
  DatabaseOutlined,
  CloudUploadOutlined,
  ThunderboltOutlined,
  CalendarOutlined,
  SafetyOutlined,
  CodeOutlined,
} from '@ant-design/icons';
import { t } from '../i18n';
import DataSample from './DataSample';

const { Title, Text } = Typography;
const { Panel } = Collapse;

interface ConfigViewerProps {
  extractConfig?: Record<string, unknown>;
  transformConfig?: Record<string, unknown>;
  loadConfig?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
}

const ConfigViewer: React.FC<ConfigViewerProps> = ({
  extractConfig,
  transformConfig,
  loadConfig,
  ddl,
  dag,
}) => {
  const renderExtractConfig = () => {
    if (!extractConfig) return null;

    const source = (extractConfig.source_metadata || extractConfig.source) as Record<string, unknown> || {};
    const content = (extractConfig.content_metadata || extractConfig.content) as Array<Record<string, unknown>> || [];
    const sampleRecords = (extractConfig as Record<string, unknown>).sample_records as unknown[] | undefined;

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Descriptions title={<Title level={4}><DatabaseOutlined /> {t('configViewer.source')}</Title>} bordered column={2}>
            <Descriptions.Item label={t('configViewer.sourceType')}>
              <Tag color="blue">{source.source_type as string || 'N/A'}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label={t('configViewer.sourcePath')}>
              <Text code>{source.connection_string as string || source.table_name as string || 'N/A'}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="Bucket/Database">
              {source.bucket_name as string || source.database_name as string || 'N/A'}
            </Descriptions.Item>
            <Descriptions.Item label="Тип контента">
              {content.length > 0 && content[0].content_type ? (
                <Tag color="green">{content[0].content_type as string}</Tag>
              ) : 'N/A'}
            </Descriptions.Item>
            <Descriptions.Item label="Количество файлов/таблиц" span={2}>
              <Tag color="purple">{content.length}</Tag>
            </Descriptions.Item>
          </Descriptions>

          {content.length > 0 && content[0].metamodel ? (
            <Collapse style={{ marginTop: 16 }}>
              <Panel header="Схема данных (metamodel)" key="1">
                <pre style={{ maxHeight: 300, overflow: 'auto', background: '#0B0F14', color: '#F5F7FF', padding: 12, border: '1px solid #1D2B44', borderRadius: 8 }}>
                  {JSON.stringify(content[0].metamodel, null, 2)}
                </pre>
              </Panel>
            </Collapse>
          ) : null}
        </Card>

        <DataSample records={sampleRecords} title="Семпл данных" />
      </Space>
    );
  };

  const renderTransformConfig = () => {
    if (!transformConfig) return null;

    const config = (transformConfig.config || transformConfig) as Record<string, unknown>;

    return (
      <Card>
        <Descriptions title={<Title level={4}><ThunderboltOutlined /> {t('configViewer.transformation')}</Title>} bordered column={2}>
          <Descriptions.Item label="Ключи идентификации">
            {Array.isArray(config.identity_keys) && config.identity_keys.length > 0 ? (
              <Space>
                {config.identity_keys.map((key: string) => (
                  <Tag key={key} color="cyan">{key}</Tag>
                ))}
              </Space>
            ) : 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Режим обработки">
            <Tag color="orange">{config.processing_mode as string || 'batch'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Размер батча">
            {config.batch_size as string || (config.resources as Record<string, unknown>)?.parallel_workers as string || 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Параллельные воркеры">
            {(config.resources as Record<string, unknown>)?.parallel_workers as string || config.max_workers as string || 'N/A'}
          </Descriptions.Item>
        </Descriptions>

        {config.validation_rules && Array.isArray(config.validation_rules) && config.validation_rules.length > 0 ? (
          <Collapse style={{ marginTop: 16 }}>
            <Panel header={`Правила валидации (${config.validation_rules.length})`} key="1">
              <pre style={{ maxHeight: 300, overflow: 'auto', background: '#0B0F14', color: '#F5F7FF', padding: 12, border: '1px solid #1D2B44', borderRadius: 8 }}>
                {JSON.stringify(config.validation_rules, null, 2)}
              </pre>
            </Panel>
          </Collapse>
        ) : null}
      </Card>
    );
  };

  const renderLoadConfig = () => {
    if (!loadConfig) return null;

    const config = (loadConfig.config || loadConfig) as Record<string, unknown>;
    const targetType = (config.target_storage_type as Record<string, unknown>)?.storage_type as string ||
                      config.target_storage_type as string;
    const targetExplanation = (config.target_storage_type as Record<string, unknown>)?.explanation as string | undefined;
    const databaseExplanation = config.database_explanation as string | undefined;
    const partitioning = (config.partitioning || {}) as Record<string, unknown>;
    const compression = (config.compression || {}) as Record<string, unknown>;
    const batchConfig = (config.batch_config || {}) as Record<string, unknown>;

    return (
      <Card>
        <Descriptions title={<Title level={4}><CloudUploadOutlined /> Конфигурация загрузки</Title>} bordered column={2}>
          <Descriptions.Item label={t('configViewer.targetType')}>
            <Tag color="purple">{targetType || 'N/A'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label={t('configViewer.targetTable')}>
            <Text code>{config.table_name as string || 'N/A'}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="Пояснение" span={2}>
            {targetExplanation || 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Пояснение к базе" span={2}>
            {databaseExplanation || 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Стратегия загрузки">
            <Tag color="magenta">{config.load_strategy as string || 'append'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Размер батча">
            {batchConfig.batch_size as string || config.load_batch_size as string || config.batch_size as string || 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Партиционирование">
            {partitioning.enabled ? (
              <Tag color="green">Включено ({partitioning.partition_by as string})</Tag>
            ) : (
              <Tag>Отключено</Tag>
            )}
          </Descriptions.Item>
          <Descriptions.Item label="Сжатие">
            {compression.enabled ? (
              <Tag color="green">{compression.algorithm as string || 'gzip'}</Tag>
            ) : (
              <Tag>Отключено</Tag>
            )}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    );
  };

  const renderDagConfig = () => {
    if (!dag) return null;

    const config = (dag.config || dag) as Record<string, unknown>;
    const schedule = (config.schedule || {}) as Record<string, unknown>;

    return (
      <Card>
        <Descriptions title={<Title level={4}><CalendarOutlined /> {t('configViewer.schedule')}</Title>} bordered column={2}>
          <Descriptions.Item label="DAG ID">
            <Text code>{config.dag_id as string || 'N/A'}</Text>
          </Descriptions.Item>
          <Descriptions.Item label={t('configViewer.scheduleInterval')}>
            <Tag color="blue">{schedule.interval as string || config.schedule_interval as string || '@daily'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Дата начала">
            {schedule.start_date as string || config.start_date as string || 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Catchup">
            <Tag color={(schedule.catchup || config.catchup) ? 'green' : 'default'}>
              {(schedule.catchup || config.catchup) ? 'Включено' : 'Отключено'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Max Active Runs">
            {schedule.max_active_runs as string || config.max_active_runs as string || '1'}
          </Descriptions.Item>
          <Descriptions.Item label="Owner">
            {config.owner as string || 'data_team'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    );
  };

  const renderDdl = () => {
    if (!ddl) return null;

    const ddlText = ddl.ddl as string || JSON.stringify(ddl, null, 2);

    return (
      <Card>
        <Title level={4} style={{ color: '#F5F7FF' }}>
          <SafetyOutlined /> DDL Схема
        </Title>
        <pre style={{
          background: '#0B0F14',
          color: '#F5F7FF',
          padding: 16,
          borderRadius: 8,
          overflow: 'auto',
          maxHeight: 400,
          border: '1px solid #1D2B44',
          fontFamily: 'IBM Plex Mono, monospace',
        }}>
          {ddlText}
        </pre>
      </Card>
    );
  };

  const tabItems = [
    {
      key: 'extract',
      label: (
        <span>
          <DatabaseOutlined /> Extract
        </span>
      ),
      children: renderExtractConfig(),
    },
    {
      key: 'transform',
      label: (
        <span>
          <ThunderboltOutlined /> Transform
        </span>
      ),
      children: renderTransformConfig(),
    },
    {
      key: 'load',
      label: (
        <span>
          <CloudUploadOutlined /> Load
        </span>
      ),
      children: renderLoadConfig(),
    },
    {
      key: 'dag',
      label: (
        <span>
          <CalendarOutlined /> DAG
        </span>
      ),
      children: renderDagConfig(),
    },
    {
      key: 'ddl',
      label: (
        <span>
          <CodeOutlined /> DDL
        </span>
      ),
      children: renderDdl(),
    },
  ];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      <Tabs defaultActiveKey="extract" items={tabItems} size="large" />
    </div>
  );
};

export default ConfigViewer;
