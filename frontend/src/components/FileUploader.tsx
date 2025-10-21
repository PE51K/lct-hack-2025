import { useState } from 'react';
import { Upload, Card, Button, Alert, Space, Typography, Progress, message } from 'antd';
import { UploadOutlined, CheckCircleOutlined, CloseCircleOutlined, InboxOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';

const { Dragger } = Upload;
const { Text, Paragraph } = Typography;

interface FileUploaderProps {
  onUploadSuccess?: (bucket: string, filePath: string) => void;
}

function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{
    success: boolean;
    message: string;
    bucket?: string;
    filePath?: string;
    fileSize?: number;
  } | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('Пожалуйста, выберите файл для загрузки');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileList[0].originFileObj as File);
    formData.append('bucket', 'test-bucket');
    formData.append('folder', 'uploads');

    setUploading(true);
    setUploadResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/upload_file`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setUploadResult({
          success: true,
          message: result.message,
          bucket: result.bucket,
          filePath: result.file_path,
          fileSize: result.file_size,
        });
        message.success('Файл успешно загружен в MinIO!');

        // Notify parent component
        if (onUploadSuccess && result.bucket && result.file_path) {
          onUploadSuccess(result.bucket, result.file_path);
        }
      } else {
        setUploadResult({
          success: false,
          message: result.error_message || 'Неизвестная ошибка',
        });
        message.error('Ошибка при загрузке файла');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadResult({
        success: false,
        message: 'Не удалось загрузить файл. Проверьте подключение к серверу.',
      });
      message.error('Ошибка при загрузке файла');
    } finally {
      setUploading(false);
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    fileList: fileList,
    beforeUpload: (file) => {
      setFileList([file]);
      setUploadResult(null);
      return false; // Prevent auto upload
    },
    onRemove: () => {
      setFileList([]);
      setUploadResult(null);
    },
    showUploadList: {
      showRemoveIcon: !uploading,
    },
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <Card
      style={{
        marginBottom: 24,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
      title={
        <Space>
          <UploadOutlined />
          <span>Загрузка файла в MinIO</span>
        </Space>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="Загрузите свой файл данных"
          description={
            <Paragraph style={{ margin: 0 }}>
              Вы можете загрузить файл (XML, CSV, JSON и др.) в MinIO хранилище, а затем использовать его в ETL процессе.
              После успешной загрузки данные для подключения к MinIO будут автоматически подставлены в промпт.
            </Paragraph>
          }
          type="info"
          showIcon
        />

        <Dragger {...uploadProps} disabled={uploading}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Нажмите или перетащите файл в эту область</p>
          <p className="ant-upload-hint">
            Поддерживаются любые форматы файлов. Файл будет загружен в MinIO хранилище.
          </p>
        </Dragger>

        {fileList.length > 0 && !uploadResult && (
          <Button
            type="primary"
            onClick={handleUpload}
            loading={uploading}
            icon={<UploadOutlined />}
            size="large"
            block
          >
            {uploading ? 'Загрузка...' : 'Загрузить в MinIO'}
          </Button>
        )}

        {uploading && (
          <div>
            <Progress percent={100} status="active" showInfo={false} />
            <Text type="secondary" style={{ marginTop: 8, display: 'block', textAlign: 'center' }}>
              Загрузка файла в MinIO...
            </Text>
          </div>
        )}

        {uploadResult && (
          <Alert
            message={uploadResult.success ? 'Успешная загрузка' : 'Ошибка загрузки'}
            description={
              uploadResult.success ? (
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <div>
                    <Text strong>Bucket:</Text> <Text code>{uploadResult.bucket}</Text>
                  </div>
                  <div>
                    <Text strong>Путь к файлу:</Text> <Text code>{uploadResult.filePath}</Text>
                  </div>
                  <div>
                    <Text strong>Размер:</Text> <Text>{uploadResult.fileSize ? formatFileSize(uploadResult.fileSize) : 'N/A'}</Text>
                  </div>
                  <Paragraph style={{ marginTop: 8, marginBottom: 0 }} type="success">
                    Теперь вы можете использовать этот файл в вашем ETL процессе!
                  </Paragraph>
                </Space>
              ) : (
                <Paragraph style={{ margin: 0 }}>
                  {uploadResult.message}
                </Paragraph>
              )
            }
            type={uploadResult.success ? 'success' : 'error'}
            showIcon
            icon={uploadResult.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          />
        )}
      </Space>
    </Card>
  );
}

export default FileUploader;
