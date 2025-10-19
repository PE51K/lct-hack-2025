import { Card, Steps, Typography, Tag, Collapse, Button, Space } from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  CodeOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useState } from 'react';
import { t } from '../i18n';

const { Title, Paragraph } = Typography;
const { Panel } = Collapse;

export interface ScriptInfo {
  name: string;
  type: 'extract' | 'transform' | 'load' | 'dag' | 'config';
  status: 'pending' | 'generating' | 'generated';
  content?: string;
  filePath?: string;
}

interface ScriptGenerationProps {
  scripts: ScriptInfo[];
}

const ScriptGeneration: React.FC<ScriptGenerationProps> = ({ scripts }) => {
  const [expandedScripts, setExpandedScripts] = useState<string[]>([]);

  const getStepStatus = (status: ScriptInfo['status']) => {
    switch (status) {
      case 'generated':
        return 'finish';
      case 'generating':
        return 'process';
      case 'pending':
        return 'wait';
      default:
        return 'wait';
    }
  };

  const getIcon = (status: ScriptInfo['status']) => {
    switch (status) {
      case 'generated':
        return <CheckCircleOutlined />;
      case 'generating':
        return <SyncOutlined spin />;
      default:
        return <FileTextOutlined />;
    }
  };

  const getScriptLabel = (type: ScriptInfo['type']) => {
    switch (type) {
      case 'extract':
        return t('scriptGeneration.extractScript');
      case 'transform':
        return t('scriptGeneration.transformScript');
      case 'load':
        return t('scriptGeneration.loadScript');
      case 'dag':
        return t('scriptGeneration.dagFile');
      case 'config':
        return t('scriptGeneration.configFile');
      default:
        return type;
    }
  };

  const getStatusTag = (status: ScriptInfo['status']) => {
    switch (status) {
      case 'generated':
        return <Tag color="success">{t('scriptGeneration.generated')}</Tag>;
      case 'generating':
        return <Tag icon={<SyncOutlined spin />} color="processing">{t('scriptGeneration.generating')}</Tag>;
      default:
        return <Tag color="default">Ожидание</Tag>;
    }
  };

  return (
    <Card
      style={{
        maxWidth: 1000,
        margin: '20px auto',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Title level={4}>
        <CodeOutlined /> {t('scriptGeneration.title')}
      </Title>

      <Steps
        direction="vertical"
        current={scripts.findIndex(s => s.status !== 'generated')}
        items={scripts.map((script, index) => ({
          key: index,
          title: (
            <Space>
              {getScriptLabel(script.type)}
              {getStatusTag(script.status)}
            </Space>
          ),
          description: script.filePath && (
            <Space direction="vertical" size="small" style={{ width: '100%', marginTop: 8 }}>
              <Paragraph type="secondary" style={{ margin: 0 }}>
                Путь: <code>{script.filePath}</code>
              </Paragraph>
              {script.content && script.status === 'generated' && (
                <Collapse
                  activeKey={expandedScripts}
                  onChange={(keys) => setExpandedScripts(keys as string[])}
                >
                  <Panel
                    header={
                      <Button
                        type="link"
                        size="small"
                        icon={<EyeOutlined />}
                      >
                        {t('scriptGeneration.viewCode')}
                      </Button>
                    }
                    key={`script-${index}`}
                  >
                    <pre
                      style={{
                        background: '#1f1f1f',
                        color: '#d4d4d4',
                        padding: 16,
                        borderRadius: 4,
                        overflow: 'auto',
                        maxHeight: 400,
                        fontSize: 12,
                      }}
                    >
                      {script.content}
                    </pre>
                  </Panel>
                </Collapse>
              )}
            </Space>
          ),
          status: getStepStatus(script.status),
          icon: getIcon(script.status),
        }))}
      />
    </Card>
  );
};

export default ScriptGeneration;
