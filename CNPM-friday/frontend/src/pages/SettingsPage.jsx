import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Layout,
    Row,
    Col,
    Typography,
    Button,
    Card,
    Avatar,
    Form,
    Input,
    Divider,
    message,
    Modal,
    Space,
    Tag
} from 'antd';
import {
    ArrowLeftOutlined,
    EditOutlined,
    UserOutlined,
    LockOutlined,
    MailOutlined
} from '@ant-design/icons';
import { useAuth } from '../components/AuthContext';

const { Title, Text } = Typography;
const { Content } = Layout;

const roles = [
    { name: 'Admin', dotColor: '#f5222d' },
    { name: 'Staff', dotColor: '#faad14' },
    { name: 'Lecturer', dotColor: '#1890ff' },
    { name: 'Student', dotColor: '#52c41a' }
];

const STORAGE_BASE_KEYS = {
    profile: 'user_profile',
    avatar: 'user_avatar'
};

const canUseStorage = () => typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';

const buildScopedKey = (baseKey, user) => {
    const identifier = user?.id || user?.email;
    return identifier ? `${baseKey}_${identifier}` : `${baseKey}_default`;
};

const readStoredProfile = (storageKey) => {
    if (!canUseStorage() || !storageKey) {
        return null;
    }
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) {
        return null;
    }
    try {
        return JSON.parse(raw);
    } catch (_err) {
        window.localStorage.removeItem(storageKey);
        return null;
    }
};

const readStoredAvatar = (storageKey, fallback) => {
    if (!canUseStorage() || !storageKey) {
        return fallback;
    }
    const storedValue = window.localStorage.getItem(storageKey);
    return storedValue || fallback;
};

const SettingsPage = () => {
    const navigate = useNavigate();
    const { user, updateUser } = useAuth();
    const fileInputRef = useRef(null);
    const [formProfile] = Form.useForm();
    const [formPassword] = Form.useForm();

    const defaultProfile = useMemo(() => ({
        name: user?.full_name || 'Tong duc huy',
        email: user?.email || 'Test@gmail.com',
        phone: user?.phone || '0495558839'
    }), [user]);

    const authAvatar = user?.avatar_url || null;
    const profileStorageKey = buildScopedKey(STORAGE_BASE_KEYS.profile, user);
    const avatarStorageKey = buildScopedKey(STORAGE_BASE_KEYS.avatar, user);

    const [userData, setUserData] = useState(defaultProfile);
    const [avatarUrl, setAvatarUrl] = useState(authAvatar);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);

    useEffect(() => {
        const stored = readStoredProfile(profileStorageKey);
        if (stored) {
            setUserData({ ...defaultProfile, ...stored });
        } else {
            setUserData(defaultProfile);
        }
    }, [profileStorageKey, defaultProfile]);

    useEffect(() => {
        const storedAvatar = readStoredAvatar(avatarStorageKey, authAvatar);
        setAvatarUrl(storedAvatar);
    }, [avatarStorageKey, authAvatar]);

    useEffect(() => {
        if (!canUseStorage()) {
            return;
        }
        const payload = { ...userData, _owner: user?.email || null };
        window.localStorage.setItem(profileStorageKey, JSON.stringify(payload));
        window.localStorage.setItem(STORAGE_BASE_KEYS.profile, JSON.stringify(payload));
        window.dispatchEvent(new CustomEvent('profile-updated', { detail: { profile: payload } }));
    }, [userData, profileStorageKey]);

    useEffect(() => {
        if (!canUseStorage()) {
            return;
        }
        if (avatarUrl) {
            window.localStorage.setItem(avatarStorageKey, avatarUrl);
            window.localStorage.setItem(STORAGE_BASE_KEYS.avatar, avatarUrl);
            window.dispatchEvent(new CustomEvent('avatar-updated', { detail: { avatarUrl } }));
        } else {
            window.localStorage.removeItem(avatarStorageKey);
            window.localStorage.removeItem(STORAGE_BASE_KEYS.avatar);
        }
    }, [avatarUrl, avatarStorageKey]);

    const handleFileChange = (event) => {
        const file = event.target.files?.[0];
        if (!file) {
            return;
        }
        const reader = new FileReader();
        reader.onloadend = () => {
            const nextAvatar = reader.result?.toString() || null;
            setAvatarUrl(nextAvatar);
            if (nextAvatar) {
                updateUser({ avatar_url: nextAvatar });
            }
            message.success('Avatar updated');
        };
        reader.readAsDataURL(file);
    };

    const handleUpdateProfile = (values) => {
        setUserData((prev) => ({ ...prev, ...values }));
        updateUser({
            full_name: values.name || user?.full_name,
            email: values.email || user?.email,
        });
        message.success('Profile updated successfully');
        setIsEditModalOpen(false);
    };

    const handleUpdatePassword = () => {
        formPassword
            .validateFields()
            .then(() => {
                message.success('Password updated successfully');
                formPassword.resetFields();
            })
            .catch(() => {
                message.error('Please fill in the form completely');
            });
    };

    return (
        <Layout style={{ minHeight: '100vh', padding: '40px', background: '#fff' }}>
            <Content style={{ maxWidth: 1200, margin: '0 auto', width: '100%' }}>
                <Title level={1} style={{ fontWeight: 600 }}>User profile & Settings</Title>
                <Divider />

                <Button
                    type="text"
                    icon={<ArrowLeftOutlined />}
                    onClick={() => navigate('/dashboard')}
                    style={{ marginBottom: 32, fontSize: 16, padding: 0 }}
                >
                    Back to dashboard
                </Button>

                <Row gutter={[24, 24]}>
                    <Col xs={24} lg={12}>
                        <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none', height: '100%' }}>
                            <Title level={4} style={{ marginBottom: 24 }}>Profile overview</Title>
                            <Row gutter={16} align="middle">
                                <Col span={10} style={{ textAlign: 'center' }}>
                                    <Avatar
                                        size={140}
                                        shape="square"
                                        src={avatarUrl}
                                        icon={!avatarUrl && <UserOutlined />}
                                        style={{ borderRadius: 12, background: '#ccc' }}
                                    />
                                    <Button size="small" style={{ marginTop: 12, borderRadius: 20 }} onClick={() => fileInputRef.current?.click()}>
                                        Change avatar
                                    </Button>
                                    <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
                                </Col>
                                <Col span={14}>
                                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                                        <div>
                                            <Text strong>Name:</Text>
                                            <Text style={{ marginLeft: 8 }}>{userData.name}</Text>
                                        </div>
                                        <div>
                                            <Text strong>Email:</Text>
                                            <Text style={{ marginLeft: 8 }}>{userData.email}</Text>
                                        </div>
                                        <div>
                                            <Text strong>Phone:</Text>
                                            <Text style={{ marginLeft: 8 }}>{userData.phone}</Text>
                                        </div>
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

                    <Col xs={24} lg={12}>
                        <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none', height: '100%' }}>
                            <Title level={4} style={{ marginBottom: 24 }}>Change Password</Title>
                            <Form form={formPassword} layout="horizontal" labelCol={{ span: 9 }}>
                                <Form.Item label={<Text strong>Current password</Text>} name="current" rules={[{ required: true }]}>
                                    <Input.Password style={{ borderRadius: 8 }} />
                                </Form.Item>
                                <Form.Item label={<Text strong>New password</Text>} name="new" rules={[{ required: true }]}>
                                    <Input.Password style={{ borderRadius: 8 }} />
                                </Form.Item>
                                <Form.Item label={<Text strong>Confirm password</Text>} name="confirm" rules={[{ required: true }]}>
                                    <Input.Password style={{ borderRadius: 8 }} />
                                </Form.Item>
                                <div style={{ textAlign: 'center', marginTop: 10 }}>
                                    <Button type="default" icon={<LockOutlined />} style={{ borderRadius: 20 }} onClick={handleUpdatePassword}>
                                        update password
                                    </Button>
                                </div>
                            </Form>
                        </Card>
                    </Col>
                </Row>

                <Row style={{ marginTop: 24 }}>
                    <Col span={24}>
                        <Card style={{ background: '#f5f5f5', borderRadius: 24, border: 'none' }}>
                            <Title level={4} style={{ marginBottom: 20 }}>Assigned Roles</Title>
                            <Space wrap size={12}>
                                {roles.map((role) => (
                                    <Tag
                                        key={role.name}
                                        style={{
                                            backgroundColor: '#fff',
                                            color: '#000',
                                            borderRadius: 20,
                                            padding: '5px 18px',
                                            border: '1px solid #d9d9d9',
                                            fontSize: 14
                                        }}
                                    >
                                        <span
                                            style={{
                                                display: 'inline-block',
                                                width: 8,
                                                height: 8,
                                                backgroundColor: role.dotColor,
                                                borderRadius: '50%',
                                                marginRight: 8
                                            }}
                                        />
                                        {role.name}
                                    </Tag>
                                ))}
                            </Space>
                        </Card>
                    </Col>
                </Row>
            </Content>

            <Modal
                title="Edit Profile Information"
                open={isEditModalOpen}
                onCancel={() => setIsEditModalOpen(false)}
                onOk={() => formProfile.submit()}
            >
                <Form form={formProfile} layout="vertical" onFinish={handleUpdateProfile}>
                    <Form.Item name="name" label="Full Name" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="email" label="Email Address" rules={[{ required: true, type: 'email' }]}>
                        <Input prefix={<MailOutlined />} />
                    </Form.Item>
                    <Form.Item name="phone" label="Phone Number">
                        <Input />
                    </Form.Item>
                </Form>
            </Modal>
        </Layout>
    );
};

export default SettingsPage;
