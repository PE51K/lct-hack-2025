import { useState } from 'react';
import InputForm from './components/InputForm';
import ProgressBar from './components/ProgressBar';
import CreationReport from './components/CreationReport';
import FeedbackForm from './components/FeedbackForm';
import DeploymentProgress from './components/DeploymentProgress';
import DeploymentReport from './components/DeploymentReport';
import { createETL, updateETL, publishETL, type CreateETLRequest, type Feedback, type ThreadUserIds, type ETLResponse } from './services/api';

type Step = 'input' | 'generating' | 'report' | 'feedback' | 'updating' | 'publishing' | 'published';

function App() {
  const [step, setStep] = useState<Step>('input');
  const [ids, setIds] = useState<ThreadUserIds | null>(null);
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [latestResponse, setLatestResponse] = useState<ETLResponse | null>(null);
  const [deploymentMessages, setDeploymentMessages] = useState<string[]>([]);
  const [deploymentSuccess, setDeploymentSuccess] = useState<boolean>(false);

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
            setStep('report');
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

  const handleSatisfied = async () => {
    if (!ids) return;
    setStep('publishing');
    setDeploymentMessages([]);

    try {
      for await (const response of publishETL({ ids })) {
        setDeploymentMessages(prev => [...prev, response.processing_message]);
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

  const renderStep = () => {
    switch (step) {
      case 'input':
        return <InputForm onSubmit={handleCreate} />;
      case 'generating':
      case 'updating':
        return <ProgressBar messages={progressMessages} isComplete={false} />;
      case 'report':
        return (
          <CreationReport
            extractConfig={latestResponse?.extract_config}
            transformConfig={latestResponse?.transform_config}
            loadConfig={latestResponse?.load_config}
            ddl={latestResponse?.ddl}
            dag={latestResponse?.dag}
            onSatisfied={handleSatisfied}
            onNotSatisfied={handleNotSatisfied}
          />
        );
      case 'feedback':
        return <FeedbackForm onSubmit={handleFeedbackSubmit} onCancel={handleFeedbackCancel} />;
      case 'publishing':
        return <DeploymentProgress messages={deploymentMessages} isComplete={false} />;
      case 'published':
        return <DeploymentReport success={deploymentSuccess} messages={deploymentMessages} />;
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div>
      <h1>AI Data Assistant</h1>
      {renderStep()}
    </div>
  );
}

export default App;
