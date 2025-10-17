import { Card, Form, Input, Button, Space, Typography, Divider } from 'antd';
import { SendOutlined, CloseCircleOutlined, MessageOutlined } from '@ant-design/icons';
import type { Feedback } from '../services/api';
import { t } from '../i18n';

const { TextArea } = Input;
const { Title, Paragraph } = Typography;

interface FeedbackFormProps {
  onSubmit: (feedback: Feedback) => void;
  onCancel: () => void;
}

const FeedbackForm: React.FC<FeedbackFormProps> = ({ onSubmit, onCancel }) => {
  const [form] = Form.useForm();

  const handleSubmit = (values: { overall?: string }) => {
    onSubmit({
      overall: values.overall || undefined,
      items: [],
    });
  };

  return (
    <Card
      style={{
        maxWidth: 700,
        margin: '0 auto',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={2}>
            <MessageOutlined /> {t('feedbackForm.title')}
          </Title>
          <Paragraph type="secondary">
            {t('feedbackForm.description')}
          </Paragraph>
        </div>

        <Divider />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          size="large"
        >
          <Form.Item
            name="overall"
            label="Комментарий и пожелания по конфигурации"
            rules={[
              {
                required: true,
                message: 'Пожалуйста, опишите требуемые изменения',
              },
            ]}
          >
            <TextArea
              rows={6}
              placeholder={t('feedbackForm.placeholder')}
            />
          </Form.Item>

          <Space style={{ width: '100%', marginTop: 20 }} size="middle">
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              icon={<SendOutlined />}
              style={{ flex: 1 }}
              block
            >
              {t('feedbackForm.submitButton')}
            </Button>
            <Button
              danger
              size="large"
              icon={<CloseCircleOutlined />}
              onClick={onCancel}
              style={{ flex: 1 }}
              block
            >
              Отмена
            </Button>
          </Space>
        </Form>
      </Space>
    </Card>
  );
};

export default FeedbackForm;