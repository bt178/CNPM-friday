import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { Layout, Row, Col, Typography, Button, Card, Avatar, Form, Input, Divider, message, Modal, Space, Tag } from 'antd';
import { ArrowLeftOutlined, EditOutlined, UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const UserProfile = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [formProfile] = Form.useForm();
  const [formPassword] = Form.useForm();
  
  // 1. Khởi tạo dữ liệu từ localStorage để không bị mất khi F5
  const [userData, setUserData] = useState(() => {
    const savedData = localStorage.getItem('user_profile');
    return savedData ? JSON.parse(savedData) : { 
      name: 'Tong duc huy', 
      email: 'Test@gmail.com', 
      phone: '0495558839' 
    };
  });

  const [avatarUrl, setAvatarUrl] = useState(() => localStorage.getItem('user_avatar') || null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // Danh sách vai trò 
  const [roles] = useState([
    { name: 'Admin', dotColor: '#f5222d' }, // Đỏ
    { name: 'Staff', dotColor: '#faad14' }, // Vàng
    { name: 'Lecturer', dotColor: '#1890ff' }, // Xanh dương
    { name: 'Student', dotColor: '#52c41a' }  // Xanh lá
  ]);

  // 2. Theo dõi thay đổi userData để lưu trữ
  useEffect(() => {
    localStorage.setItem('user_profile', JSON.stringify(userData));
  }, [userData]);

  // Thay đổi ảnh đại diện
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        return message.error('Vui lòng chọn tệp hình ảnh!');
      }
      const previewUrl = URL.createObjectURL(file);
      setAvatarUrl(previewUrl);
      localStorage.setItem('user_avatar', previewUrl);
      message.success('Đã cập nhật ảnh đại diện mới!');
    }
  };

  // Cập nhật thông tin
  const onUpdateProfile = (values) => {
    setUserData(values);
    message.success('Cập nhật thông tin thành công!');
    setIsEditModalOpen(false);
  };

  // Đổi mật khẩu
  const onUpdatePassword = (values) => {
    message.success('Đã gửi yêu cầu cập nhật mật khẩu!');
    formPassword.resetFields();
  };

  return (
    <Layout style={{ minHeight: '100vh', padding: '40px', background: '#fff' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', width: '100%' }}>
        <Title level={1} style={{ fontWeight: 600 }}>User profile & Settings</Title>
        <Divider />
        
        <Button 
          type="text" 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/dashboard')} 
          style={{ marginBottom: 32, fontSize: '16px', padding: 0 }}
        >
          back to dashboard
        </Button>

        <Row gutter={[24, 24]}>
          {/* CỘT 1: PROFILE OVERVIEW */}
          <Col xs={24} lg={12}>
            <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none', height: '100%' }}>
              <Title level={4} style={{ marginBottom: 24 }}>Profile overview</Title>
              <Row gutter={16}>
                <Col span={10} style={{ textAlign: 'center' }}>
                  <Avatar 
                    size={140} 
                    shape="square" 
                    src={avatarUrl}
                    icon={!avatarUrl && <UserOutlined />} 
                    style={{ borderRadius: 12, background: '#ccc' }} 
                  />
                  <Button 
                    size="small" 
                    style={{ marginTop: 12, borderRadius: 20 }}
                    onClick={() => fileInputRef.current.click()}
                  >
                    Change avatar
                  </Button>
                  <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
                </Col>
                <Col span={14}>
                  <Space direction="vertical" size={16} style={{ width: '100%' }}>
                    <div><Text strong>Name:</Text><Text style={{ marginLeft: 8 }}>{userData.name}</Text></div>
                    <div><Text strong>Email:</Text><Text style={{ marginLeft: 8 }}>{userData.email}</Text></div>
                    <div><Text strong>Phone:</Text><Text style={{ marginLeft: 8 }}>{userData.phone}</Text></div>
                    <Button 
                      icon={<EditOutlined />} 
                      style={{ borderRadius: 20, marginTop: 10 }}
                      onClick={() => {
                        formProfile.setFieldsValue(userData);
                        setIsEditModalOpen(true);
                      }}
                    >
                      Edit profile
                    </Button>
                  </Space>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* CỘT 2: CHANGE PASSWORD */}
          <Col xs={24} lg={12}>
            <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none', height: '100%' }}>
              <Title level={4} style={{ marginBottom: 24 }}>Change Password</Title>
              <Form form={formPassword} layout="horizontal" labelCol={{ span: 9 }} onFinish={onUpdatePassword}>
                <Form.Item label={<Text strong>Current password</Text>} name="current" rules={[{required: true}]}>
                  <Input.Password style={{ borderRadius: 8 }} />
                </Form.Item>
                <Form.Item label={<Text strong>New password</Text>} name="new" rules={[{required: true, min: 6}]}>
                  <Input.Password style={{ borderRadius: 8 }} />
                </Form.Item>
                <Form.Item label={<Text strong>Confirm password</Text>} name="confirm" rules={[{required: true}]}>
                  <Input.Password style={{ borderRadius: 8 }} />
                </Form.Item>
                <div style={{ textAlign: 'center', marginTop: 10 }}>
                  <Button type="default" icon={<LockOutlined />} htmlType="submit" style={{ borderRadius: 20 }}>
                    update password
                  </Button>
                </div>
              </Form>
            </Card>
          </Col>
        </Row>

        {/* HÀNG 2: ASSIGNED ROLES */}
        <Row style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none' }}>
              <Title level={4} style={{ marginBottom: 20 }}>Assigned Roles</Title>
              <Space wrap size={12}>
                {roles.map(role => (
                  <Tag 
                    key={role.name} 
                    style={{ 
                      backgroundColor: 'white', 
                      color: 'black', 
                      borderRadius: 20, 
                      padding: '5px 18px', 
                      border: '1px solid #d9d9d9',
                      fontSize: '14px',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                  >
                    <span style={{ 
                      display: 'inline-block',
                      width: 8, height: 8, 
                      backgroundColor: role.dotColor, 
                      borderRadius: '50%', 
                      marginRight: 8 
                    }} />
                    {role.name}
                  </Tag>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      </div>

      {/* MODAL EDIT PROFILE */}
      <Modal 
        title="Edit Profile Information" 
        open={isEditModalOpen} 
        onCancel={() => setIsEditModalOpen(false)} 
        onOk={() => formProfile.submit()}
      >
        <Form form={formProfile} layout="vertical" onFinish={onUpdateProfile}>
          <Form.Item name="name" label="Full Name" rules={[{required: true}]}><Input /></Form.Item>
          <Form.Item name="email" label="Email Address" rules={[{required: true, type: 'email'}]}><Input prefix={<MailOutlined />} /></Form.Item>
          <Form.Item name="phone" label="Phone Number"><Input /></Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
};

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<UserProfile />} />
      <Route path="/dashboard" element={<div style={{padding: 50}}>Trang Dashboard</div>} />
    </Routes>
  </Router>
);

export default App;
