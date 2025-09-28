import { useState } from 'react';
import InputForm from './components/InputForm';
import ProgressBar from './components/ProgressBar';
import CreationReport from './components/CreationReport';
import FeedbackForm from './components/FeedbackForm';
import DeploymentProgress from './components/DeploymentProgress';
import DeploymentReport from './components/DeploymentReport';
import { generateETL, updateETL, executeETL, type GenerateETLRequest, type Feedback, type ThreadUserIds, type GenerateETLResponse } from './services/api';

type Step = 'input' | 'generating' | 'report' | 'feedback' | 'updating' | 'deploying' | 'deployed';

function App() {
  const [step, setStep] = useState<Step>('input');
  const [ids, setIds] = useState<ThreadUserIds | null>(null);
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [latestResponse, setLatestResponse] = useState<GenerateETLResponse | null>(null);
  const [deploymentMessages, setDeploymentMessages] = useState<string[]>([]);
  const [deploymentSuccess, setDeploymentSuccess] = useState<boolean>(false);

  const handleGenerate = async (request: GenerateETLRequest) => {
    setIds(request.ids);
    setStep('generating');
    setProgressMessages([]);
    setLatestResponse(null);

    try {
      for await (const response of generateETL(request)) {
        setProgressMessages(prev => [...prev, response.message]);
        if (response.done) {
          setLatestResponse(response);
          setStep('report');
        }
      }
    } catch (error) {
      console.error('Generation failed:', error);
      setProgressMessages(prev => [...prev, 'Generation failed']);
    }
  };

  const handleSatisfied = async () => {
    if (!ids) return;
    setStep('deploying');
    setDeploymentMessages([]);

    try {
      for await (const response of executeETL({ ids })) {
        setDeploymentMessages(prev => [...prev, response.message]);
        if (response.done) {
          setDeploymentSuccess(response.success);
          setStep('deployed');
        }
      }
    } catch (error) {
      console.error('Execution failed:', error);
      setDeploymentMessages(prev => [...prev, 'Execution failed']);
    }
  };

  const handleNotSatisfied = () => {
    setStep('feedback');
  };

  const handleFeedbackSubmit = async (feedback: Feedback) => {
    if (!ids) return;
    setStep('updating');
    setProgressMessages([]);

    try {
      for await (const response of updateETL({ feedback, ids })) {
        setProgressMessages(prev => [...prev, response.message]);
        if (response.done) {
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
        return <InputForm onSubmit={handleGenerate} />;
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
      case 'deploying':
        return <DeploymentProgress messages={deploymentMessages} isComplete={false} />;
      case 'deployed':
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
