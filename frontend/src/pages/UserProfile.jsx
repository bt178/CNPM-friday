import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Row, Col, Typography, Button, Card, Avatar, Form, Input, Divider, message, Modal, Space, Tag } from 'antd';
import { ArrowLeftOutlined, EditOutlined, UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const UserProfile = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [formProfile] = Form.useForm();
  const [formPassword] = Form.useForm();

  // Khởi tạo state từ Local Storage
  const [userData, setUserData] = useState(() => {
    const savedData = localStorage.getItem('user_profile');
    return savedData ? JSON.parse(savedData) : {
      name: 'Tong duc huy',
      email: 'Test@gmail.com',
      phone: '0495558839',
      role: 'Student' //vai trò mặc định 
    };
  });

  const [avatarUrl, setAvatarUrl] = useState(() => localStorage.getItem('user_avatar') || null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const roles = [
    { name: 'Admin', dotColor: '#f5222d' },
    { name: 'Staff', dotColor: '#faad14' },
    { name: 'Lecturer', dotColor: '#1890ff' },
    { name: 'Student', dotColor: '#52c41a' }
  ];

  const currentRole = roles.find(r => r.name === (userData.role || 'Student')) || roles.find(r => r.name === 'Student');

  // Lưu dữ liệu mỗi khi userData thay đổi
  useEffect(() => {
    localStorage.setItem('user_profile', JSON.stringify(userData));
  }, [userData]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) { // Giới hạn 2MB
        return message.error('Ảnh quá lớn! Vui lòng chọn ảnh dưới 2MB.');
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result;
        setAvatarUrl(base64String);
        localStorage.setItem('user_avatar', base64String);
        message.success('Đã cập nhật ảnh đại diện mới!');
      };
      reader.readAsDataURL(file);
    }
  };

  const onUpdateProfile = (values) => {
    setUserData(prev => ({ ...prev, ...values }));
    message.success('Cập nhật thông tin thành công!');
    setIsEditModalOpen(false);
  };

  const handleUpdatePassword = async () => {
    try {
      const values = await formPassword.validateFields();
      if (values.new !== values.confirm) {
        return message.error('Mật khẩu xác nhận không trùng khớp!');
      }

      console.log("Đang đổi mật khẩu...", values);
      message.loading({ content: 'Đang xử lý...', key: 'updatable' });

      setTimeout(() => {
        message.success({ content: 'Đổi mật khẩu thành công!', key: 'updatable', duration: 2 });
        formPassword.resetFields();
      }, 1000);

    } catch (error) {
      //tự hiển thị lỗi
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', padding: '40px', background: '#fff' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', width: '100%' }}>
        <Title level={1} style={{ fontWeight: 600 }}>User profile & Settings</Title>
        <Divider />

        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/')}
          style={{ marginBottom: 32, fontSize: '16px', padding: 0 }}
        >
          Back to dashboard
        </Button>

        <Row gutter={[24, 24]}>
          {/* Profile Overview Card */}
          <Col xs={24} lg={12}>
            <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none', height: '100%' }}>
              <Title level={4} style={{ marginBottom: 24 }}>Profile overview</Title>
              <Row gutter={16} align="middle">
                <Col span={10} style={{ textAlign: 'center' }}>
                  <Avatar size={140} shape="square" src={avatarUrl} icon={!avatarUrl && <UserOutlined />} style={{ borderRadius: 12, background: '#ccc' }} />
                  <Button size="small" style={{ marginTop: 12, borderRadius: 20 }} onClick={() => fileInputRef.current.click()}>Change avatar</Button>
                  <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
                </Col>
                <Col span={14}>
                  <Space direction="vertical" size={16} style={{ width: '100%' }}>
                    <div><Text strong>Name:</Text><Text style={{ marginLeft: 8 }}>{userData.name}</Text></div>
                    <div><Text strong>Email:</Text><Text style={{ marginLeft: 8 }}>{userData.email}</Text></div>
                    <div><Text strong>Phone:</Text><Text style={{ marginLeft: 8 }}>{userData.phone}</Text></div>
                    <Button icon={<EditOutlined />} style={{ borderRadius: 20, marginTop: 10 }} onClick={() => { formProfile.setFieldsValue(userData); setIsEditModalOpen(true); }}>Edit profile</Button>
                  </Space>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* Password Card */}
          <Col xs={24} lg={12}>
            <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none', height: '100%' }}>
              <Title level={4} style={{ marginBottom: 24 }}>Change Password</Title>
              <Form form={formPassword} layout="horizontal" labelCol={{ span: 9 }}>
                <Form.Item label={<Text strong>Current password</Text>} name="current" rules={[{ required: true }]}><Input.Password style={{ borderRadius: 8 }} /></Form.Item>
                <Form.Item label={<Text strong>New password</Text>} name="new" rules={[{ required: true }]}><Input.Password style={{ borderRadius: 8 }} /></Form.Item>
                <Form.Item label={<Text strong>Confirm password</Text>} name="confirm" rules={[{ required: true }]}><Input.Password style={{ borderRadius: 8 }} /></Form.Item>
                <div style={{ textAlign: 'center', marginTop: 10 }}>
                  <Button type="default" icon={<LockOutlined />} style={{ borderRadius: 20 }} onClick={handleUpdatePassword}>update password</Button>
                </div>
              </Form>
            </Card>
          </Col>
        </Row>

        {/* Roles Card */}
        <Row style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none' }}>
              <Title level={4} style={{ marginBottom: 20 }}>Assigned Roles</Title>
              <Space wrap size={12}>
                <Tag style={{ backgroundColor: 'white', color: 'black', borderRadius: 20, padding: '5px 18px', border: '1px solid #d9d9d9', fontSize: '14px' }}>
                  <span style={{ display: 'inline-block', width: 8, height: 8, backgroundColor: currentRole.dotColor, borderRadius: '50%', marginRight: 8 }} />
                  {currentRole.name}
                </Tag>
              </Space>
            </Card>
          </Col>
        </Row>
      </div>

      {/* Edit Modal */}
      <Modal title="Edit Profile Information" open={isEditModalOpen} onCancel={() => setIsEditModalOpen(false)} onOk={() => formProfile.submit()}>
        <Form form={formProfile} layout="vertical" onFinish={onUpdateProfile}>
          <Form.Item name="name" label="Full Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item
            name="email"
            label="Email Address"
            rules={[
              { required: true, message: 'Please input your email!' },
              { pattern: /^[a-zA-Z0-9._%+-]+@(gmail\.com|ut\.edu\.vn)$/, message: 'Email must be @gmail.com or @ut.edu.vn' }
            ]}
          >
            <Input prefix={<MailOutlined />} />
          </Form.Item>
          <Form.Item
            name="phone"
            label="Phone Number"
            rules={[
              { required: true, message: 'Please input your phone number!' },
              { pattern: /^\d{9,10}$/, message: 'Phone number must be digits only and 9-10 characters long.' }
            ]}
          >
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
};

export default UserProfile;