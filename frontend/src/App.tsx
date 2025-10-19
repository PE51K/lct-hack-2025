import { useState, useEffect } from 'react';
import { ConfigProvider, Layout, Typography, Steps, theme, Button, Space } from 'antd';
import { SettingOutlined, ArrowLeftOutlined, DatabaseOutlined } from '@ant-design/icons';
import ruRU from 'antd/locale/ru_RU';
import InputForm from './components/InputForm';
import ProgressBar from './components/ProgressBar';
import CreationReport from './components/CreationReport';
import CredentialsForm from './components/CredentialsForm';
import FeedbackForm from './components/FeedbackForm';
import DeploymentProgress from './components/DeploymentProgress';
import DeploymentReport from './components/DeploymentReport';
import Settings from './components/Settings';
import ViewResults from './components/ViewResults';
import { createETL, createDAG, updateETL, publishETL, type CreateETLRequest, type Feedback, type ThreadUserIds, type ETLResponse } from './services/api';
import { t } from './i18n';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

type Step = 'input' | 'generating' | 'credentials' | 'creating_dag' | 'report' | 'feedback' | 'updating' | 'publishing' | 'published' | 'view_results';

function App() {
  const [step, setStep] = useState<Step>('input');
  const [ids, setIds] = useState<ThreadUserIds | null>(null);
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [latestResponse, setLatestResponse] = useState<ETLResponse | null>(null);
  const [deploymentMessages, setDeploymentMessages] = useState<string[]>([]);
  const [deploymentSuccess, setDeploymentSuccess] = useState<boolean>(false);
  const [dagId, setDagId] = useState<string>('');
  const [airflowUrl, setAirflowUrl] = useState<string>('');
  const [settingsVisible, setSettingsVisible] = useState<boolean>(false);
  const [dbCredentials, setDbCredentials] = useState<Record<string, unknown> | null>(null);

  const handleCreate = async (request: CreateETLRequest) => {
    setIds(request.ids);
    setStep('generating');
    setProgressMessages([]);
    setLatestResponse(null);

    try {
      for await (const response of createETL(request)) {
        setProgressMessages(prev => [...prev, response.processing_message]);
        if (response.processing_done) {
          if (response.success) {
            setLatestResponse(response);
            // Check if credentials are required (new 2-step workflow)
            if (response.credentials_required && response.next_step === 'create_dag') {
              setStep('credentials');
            } else {
              // Old workflow - DAG already created
              setStep('report');
            }
          } else {
            setProgressMessages(prev => [...prev, `Error: ${response.error_message || 'Unknown error'}`]);
            // Stay in generating state to show error
          }
        }
      }
    } catch (error) {
      console.error('Creation failed:', error);
      setProgressMessages(prev => [...prev, 'Creation failed']);
    }
  };

  const handleCredentialsSubmit = async (credentials: Record<string, unknown>) => {
    if (!ids || !latestResponse) return;

    // Store credentials for later use (e.g., viewing data sample)
    setDbCredentials(credentials);

    setStep('creating_dag');
    setProgressMessages(['Creating DAG with provided credentials...']);

    try {
      const response = await createDAG({
        ids,
        target_credentials: credentials,
        extract_config: latestResponse.extract_config!,
        transform_config: latestResponse.transform_config!,
        load_config: latestResponse.load_config!,
        ddl: latestResponse.ddl!,
      });

      setProgressMessages(prev => [...prev, response.processing_message]);

      if (response.success) {
        // Update latestResponse with DAG
        setLatestResponse(prev => ({
          ...prev!,
          dag: response.dag,
          load_config: response.updated_load_config || prev!.load_config,
        }));

        // Extract DAG ID from dag response
        if (response.dag) {
          const dag = response.dag as Record<string, unknown>;
          // DAG model has dag_id directly on it (not in a config sub-object)
          const extractedDagId = dag.dag_id as string;
          if (extractedDagId) {
            setDagId(extractedDagId);
            // Set Airflow URL
            setAirflowUrl(`http://localhost:8081/dags/${extractedDagId}/grid`);
          }
        }

        setStep('report');
      } else {
        setProgressMessages(prev => [...prev, `Error: ${response.error_message || 'Unknown error'}`]);
        // Go back to credentials form to retry
        setStep('credentials');
      }
    } catch (error) {
      console.error('DAG creation failed:', error);
      setProgressMessages(prev => [...prev, 'DAG creation failed']);
      setStep('credentials');
    }
  };

  const handleCredentialsCancel = () => {
    setStep('input');
    setLatestResponse(null);
    setProgressMessages([]);
  };

  const handleSatisfied = async () => {
    if (!ids) return;
    setStep('publishing');
    setDeploymentMessages([]);

    try {
      for await (const response of publishETL({ ids })) {
        console.log('[App] publishETL response:', response);
        setDeploymentMessages(prev => [...prev, response.processing_message]);

        // Extract dagId from response if available
        if (response.dag_id) {
          console.log('[App] Setting dagId from response:', response.dag_id);
          setDagId(response.dag_id);
        }

        // Extract airflowUrl from response if available
        if (response.airflow_url) {
          console.log('[App] Setting airflowUrl from response:', response.airflow_url);
          setAirflowUrl(response.airflow_url);
        }

        if (response.processing_done) {
          setDeploymentSuccess(response.success);
          setStep('published');
        }
      }
    } catch (error) {
      console.error('Publishing failed:', error);
      setDeploymentMessages(prev => [...prev, 'Publishing failed']);
    }
  };

  const handleNotSatisfied = () => {
    setStep('feedback');
  };

  const handleFeedbackSubmit = async (feedback: Feedback) => {
    if (!ids || !latestResponse) return;
    setStep('updating');
    setProgressMessages([]);

    try {
      for await (const response of updateETL({
        feedback,
        ids,
        extract_config: latestResponse.extract_config,
        transform_config: latestResponse.transform_config,
        load_config: latestResponse.load_config,
        ddl: latestResponse.ddl,
        dag: latestResponse.dag
      })) {
        setProgressMessages(prev => [...prev, response.processing_message]);
        if (response.processing_done) {
          setLatestResponse(response);
          setStep('report');
        }
      }
    } catch (error) {
      console.error('Update failed:', error);
      setProgressMessages(prev => [...prev, 'Update failed']);
    }
  };

  const handleFeedbackCancel = () => {
    setStep('report');
  };

  const handleReset = () => {
    setStep('input');
    setIds(null);
    setProgressMessages([]);
    setLatestResponse(null);
    setDeploymentMessages([]);
    setDeploymentSuccess(false);
    setDagId('');
    setAirflowUrl('');
    setDbCredentials(null);
  };

  // Extract DAG ID when latestResponse changes and has DAG
  useEffect(() => {
    if (latestResponse?.dag && !dagId) {
      const dag = latestResponse.dag as Record<string, unknown>;
      // DAG model has dag_id directly on it (not in a config sub-object)
      const extractedDagId = dag.dag_id as string;
      if (extractedDagId) {
        setDagId(extractedDagId);
        setAirflowUrl(`http://localhost:8081/dags/${extractedDagId}/grid`);
      }
    }
  }, [latestResponse, dagId]);

  const handleBack = () => {
    // Define allowed back transitions
    const backTransitions: Partial<Record<Step, Step>> = {
      credentials: 'input',
      report: 'credentials',
      feedback: 'report',
      published: 'input',
    };

    const previousStep = backTransitions[step];
    if (previousStep) {
      setStep(previousStep);
    }
  };

  const canGoBack = () => {
    return ['credentials', 'report', 'feedback', 'published'].includes(step);
  };

  const getStepNumber = () => {
    const stepMap: Record<Step, number> = {
      input: 0,
      generating: 1,
      credentials: 2,
      creating_dag: 3,
      report: 4,
      feedback: 4,
      updating: 4,
      publishing: 5,
      published: 6,
      view_results: 0,
    };
    return stepMap[step] || 0;
  };

  const renderStep = () => {
    switch (step) {
      case 'input':
        return <InputForm onSubmit={handleCreate} />;
      case 'generating':
      case 'updating':
      case 'creating_dag':
        return <ProgressBar messages={progressMessages} isComplete={false} />;
      case 'credentials':
        return latestResponse?.credentials_required ? (
          <CredentialsForm
            credentialsRequired={latestResponse.credentials_required}
            onSubmit={handleCredentialsSubmit}
            onCancel={handleCredentialsCancel}
          />
        ) : null;
      case 'report':
        return (
          <CreationReport
            extractConfig={latestResponse?.extract_config}
            transformConfig={latestResponse?.transform_config}
            loadConfig={latestResponse?.load_config}
            ddl={latestResponse?.ddl}
            dag={latestResponse?.dag}
            dagId={dagId}
            airflowUrl={airflowUrl}
            onSatisfied={handleSatisfied}
            onNotSatisfied={handleNotSatisfied}
          />
        );
      case 'feedback':
        return <FeedbackForm onSubmit={handleFeedbackSubmit} onCancel={handleFeedbackCancel} />;
      case 'publishing':
        return <DeploymentProgress messages={deploymentMessages} isComplete={false} />;
      case 'published':
        return (
          <DeploymentReport
            success={deploymentSuccess}
            messages={deploymentMessages}
            dagId={dagId}
            airflowUrl={airflowUrl}
            onCreateNew={handleReset}
            dbCredentials={dbCredentials}
          />
        );
      case 'view_results':
        return <ViewResults onClose={handleReset} />;
      default:
        return <div>Unknown step</div>;
    }
  };

  const [isMobile, setIsMobile] = useState(window.innerWidth < 576);

  // Handle responsive layout
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 576);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <ConfigProvider
      locale={ruRU}
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#0042FF',
          colorInfo: '#439EFF',
          colorSuccess: '#00E5FF',
          colorWarning: '#FFC857',
          colorError: '#FF4D6D',
          colorBgBase: '#0B0F14',
          colorBgContainer: 'rgba(11, 15, 20, 0.6)',
          colorText: '#F5F7FF',
          colorTextSecondary: '#B6C2D9',
          colorBorder: '#1D2B44',
          borderRadius: 12,
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        },
      }}
    >
      <div className="app-background">
        <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
          <Header
            className="app-header"
            style={{
              padding: '0 50px',
              position: 'sticky',
              top: 0,
              zIndex: 100,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div className="app-logo" onClick={handleReset} style={{ cursor: 'pointer' }}>
              <div className="app-logo-icon">
                <div className="app-logo-satellite"></div>
              </div>
              <Title level={3} style={{ margin: '16px 0', color: '#F5F7FF', fontWeight: 700, letterSpacing: '-0.5px' }}>
                {t('app.title')}
              </Title>
            </div>
            <Space>
              {canGoBack() && (
                <Button
                  icon={<ArrowLeftOutlined />}
                  onClick={handleBack}
                  size="large"
                  style={{ borderRadius: 8 }}
                >
                  Назад
                </Button>
              )}
              <Button
                icon={<DatabaseOutlined />}
                onClick={() => setStep('view_results')}
                size="large"
                type="default"
                style={{ borderRadius: 8 }}
              >
                Просмотр результатов
              </Button>
              <Button
                icon={<SettingOutlined />}
                onClick={() => setSettingsVisible(true)}
                size="large"
                type="text"
                style={{ borderRadius: 8 }}
              >
                Настройки
              </Button>
            </Space>
          </Header>
          <Content style={{ padding: '24px 50px', position: 'relative', zIndex: 1 }}>
            <div style={{ maxWidth: 1400, margin: '0 auto' }}>
              {step !== 'input' && (
                <div className="step-indicator">
                  <Steps
                    current={getStepNumber()}
                    direction={isMobile ? 'vertical' : 'horizontal'}
                    size={isMobile ? 'small' : 'default'}
                    responsive={false}
                    items={[
                      { title: t('steps.input') },
                      { title: t('steps.generating') },
                      { title: t('steps.credentials') },
                      { title: t('steps.creating_dag') },
                      { title: t('steps.report') },
                      { title: t('steps.publishing') },
                      { title: t('steps.published') },
                    ]}
                  />
                </div>
              )}
              {renderStep()}
            </div>
          </Content>
        </Layout>
        <Settings visible={settingsVisible} onClose={() => setSettingsVisible(false)} />
      </div>
    </ConfigProvider>
  );
}

export default App;
