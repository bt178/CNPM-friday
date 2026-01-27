import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Layout, Typography, Button, Table, Avatar, Space, Badge,
  Input, Row, Col, Tooltip, Modal, Form, InputNumber, Select, message, Menu, Tabs, Popover, Divider
} from 'antd';
import {
  SearchOutlined, UserOutlined, BookOutlined, TeamOutlined,
  EditOutlined, DeleteOutlined, PlusOutlined,
  MenuOutlined, ArrowLeftOutlined, SettingOutlined, BellOutlined,
  LogoutOutlined
} from '@ant-design/icons';

// Import services
import { subjectService, classService, userService } from '../services/api';
import { useAuth } from '../components/AuthContext';

const { Title, Text } = Typography;
const { Header, Sider, Content } = Layout;

const AdminDashboard = () => {
  const [form] = Form.useForm();
  const { logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('1'); // 1: Môn học, 2: Học kỳ, 3: Người dùng

  // Notification State
  const [isNotificationOpen, setNotificationOpen] = useState(false);
  const notificationAnchorRef = useRef(null);

  const notifications = useMemo(() => ([
    {
      id: 1,
      title: 'System Update',
      description: 'System maintenance scheduled for 2 AM.',
      timeAgo: '1 hour ago',
    },
    {
      id: 2,
      title: 'New User Registered',
      description: 'User "John Doe" has set up an account.',
      timeAgo: '2 hours ago',
    },
    {
      id: 3,
      title: 'Server Load High',
      description: 'CPU usage exceeded 80% for 5 minutes.',
      timeAgo: '3 hours ago',
    },
  ]), []);

  const notificationContent = (
    <div style={{ width: 320 }}>
      <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 8 }}>Notifications</div>
      <Divider style={{ margin: '0 0 12px' }} />
      <div>
        {notifications.map((item, index) => (
          <div key={item.id} style={{ padding: '8px 0' }}>
            <div style={{ display: 'flex', gap: 12 }}>
              <Avatar shape="square" size={36} style={{ backgroundColor: '#f0f0f0', color: '#8c8c8c' }}>
                <BellOutlined />
              </Avatar>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <Text strong style={{ display: 'block' }}>{item.title}</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>{item.description}</Text>
                  </div>
                  <Text type="secondary" style={{ fontSize: 11 }}>{item.timeAgo}</Text>
                </div>
              </div>
            </div>
            {index !== notifications.length - 1 && <Divider style={{ margin: '12px 0' }} />}
          </div>
        ))}
      </div>
      <Divider style={{ margin: '8px 0 12px' }} />
      <Button type="link" block onClick={() => setNotificationOpen(false)}>
        View all Notifications
      </Button>
    </div>
  );

  // Trạng thái dữ liệu
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  // Trạng thái truy vấn
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });

  // Trạng thái Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingKey, setEditingKey] = useState(null);

  // --- LẤY DỮ LIỆU ---
  const fetchData = async () => {
    setLoading(true);
    try {
      let res;
      const params = {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        search: searchText
      };

      if (selectedKey === '1') {
        res = await subjectService.getAll(params);
      } else if (selectedKey === '2') {
        res = await classService.getAll(params);
      } else if (selectedKey === '3') {
        res = await userService.getAll(params);
      }

      // Kiểm tra định dạng
      const resultData = Array.isArray(res.data) ? res.data : [];
      setData(resultData);

      // Vì backend chưa trả về tổng số lượng, nên ta giả lập phân trang hoặc giả định đơn giản
      // Để phân trang thực tế, phản hồi backend cần bao gồm tổng số.
      // Triển khai hiện tại trả về toàn bộ danh sách hoặc danh sách giới hạn.
      // Ta sẽ giả định độ dài dữ liệu là tổng số cho phiên bản đơn giản này trừ khi backend hỗ trợ đếm.
      setTotal(resultData.length); // Placeholder, improving later

    } catch (err) {
      console.error("API Error:", err);
      message.error("Error: Unable to load data.");
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedKey, pagination.current, searchText]);

  // --- HÀNH ĐỘNG ---
  const handleDelete = (id) => {
    Modal.confirm({
      title: 'Confirm Delete?',
      content: 'This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        try {
          if (selectedKey === '1') await subjectService.delete(id);
          else if (selectedKey === '2') await classService.delete(id);
          // Người dùng thường được vô hiệu hóa mềm, đang chờ triển khai

          message.success('Deleted successfully');
          fetchData();
        } catch (err) {
          message.error("Failed to delete data!");
        }
      }
    });
  };

  const handleCreateOrUpdate = async (values) => {
    try {
      if (selectedKey === '1') {
        if (editingKey) await subjectService.update(editingKey, values);
        else await subjectService.create(values);
      } else if (selectedKey === '2') {
        if (editingKey) await classService.update(editingKey, values);
        else await classService.create(values);
      }
      // Tạo người dùng thường liên quan đến nhiều logic hơn (mật khẩu), giữ đơn giản cho lúc này

      message.success(editingKey ? 'Updated successfully' : 'Created successfully');
      setIsModalOpen(false);
      fetchData();
    } catch (err) {
      message.error(err.message || "Error: Please check input info.");
    }
  };

  // --- CỘT ---
  const getColumns = () => {
    const commonActions = {
      title: 'Actions',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Tooltip title="Edit">
            <Button size="small" icon={<EditOutlined />} onClick={() => {
              setEditingKey(record.subject_id || record.class_id || record.user_id);
              form.setFieldsValue(record);
              setIsModalOpen(true);
            }} />
          </Tooltip>
          <Tooltip title="Delete">
            <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.subject_id || record.class_id || record.user_id)} />
          </Tooltip>
        </Space>
      )
    };

    if (selectedKey === '1') { // MÔN HỌC
      return [
        { title: 'Course Code', dataIndex: 'subject_code', key: 'subject_code' },
        { title: 'Subject Name', dataIndex: 'subject_name', key: 'subject_name' },
        { title: 'Dept ID', dataIndex: 'dept_id', key: 'dept_id', align: 'center' },
        commonActions
      ];
    } else if (selectedKey === '2') { // LỚP HỌC
      return [
        { title: 'Class Code', dataIndex: 'class_code', key: 'class_code' },
        { title: 'Subject', dataIndex: 'subject_name', key: 'subject_name' },
        { title: 'Lecturer', dataIndex: 'lecturer_name', key: 'lecturer_name' },
        commonActions
      ];
    } else if (selectedKey === '3') { // NGƯỜI DÙNG
      return [
        { title: 'Email', dataIndex: 'email', key: 'email' },
        { title: 'Full Name', dataIndex: 'full_name', key: 'full_name' },
        { title: 'Role', dataIndex: 'role_name', key: 'role_name' },
        { title: 'Status', dataIndex: 'is_active', key: 'is_active', render: (val) => val ? <Badge status="success" text="Active" /> : <Badge status="error" text="Inactive" /> }
      ];
    }
    return [];
  };

  const getTitle = () => {
    switch (selectedKey) {
      case '1': return 'Subject Management';
      case '2': return 'Class Management';
      case '3': return 'User Management';
      default: return 'Dashboard';
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={240} theme="light" collapsible collapsed={collapsed} trigger={null} style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuOutlined /> : <ArrowLeftOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '18px' }}
          />
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[selectedKey]}
          onClick={(e) => { setSelectedKey(e.key); setPagination({ ...pagination, current: 1 }); }}
          items={[
            { key: '1', icon: <BookOutlined />, label: 'Subject Management' },
            { key: '2', icon: <TeamOutlined />, label: 'Class Management' },
            { key: '3', icon: <UserOutlined />, label: 'User Management' },
            { key: '4', icon: <SettingOutlined />, label: 'System Settings' },
          ]}
        />
      </Sider>

      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <Title level={4} style={{ margin: 0 }}>CollabSphere Admin System</Title>
          <Space size="large">
            <div ref={notificationAnchorRef} style={{ display: 'inline-flex' }}>
              <Popover
                content={notificationContent}
                trigger="click"
                placement="bottomRight"
                open={isNotificationOpen}
                onOpenChange={setNotificationOpen}
                overlayStyle={{ padding: 0 }}
                arrowPointAtCenter
                getPopupContainer={() => notificationAnchorRef.current || document.body}
              >
                <Badge dot offset={[-5, 5]}>
                  <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
                </Badge>
              </Popover>
            </div>
            <Space>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
              <Text strong>Administrator</Text>
            </Space>
            <Button icon={<LogoutOutlined />} onClick={logout}>
              Sign out
            </Button>
          </Space>
        </Header>

        <Content style={{ padding: '24px' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', minHeight: '80vh' }}>
            <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
              <Col>
                <Title level={3} style={{ margin: 0 }}>{getTitle()}</Title>
              </Col>
              <Col>
                <Space>
                  <Input
                    placeholder="Search..."
                    prefix={<SearchOutlined />}
                    onChange={e => setSearchText(e.target.value)}
                    allowClear
                    style={{ width: 300, borderRadius: '6px' }}
                  />
                  {selectedKey !== '3' && (
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingKey(null); form.resetFields(); setIsModalOpen(true); }} size="large">
                      Add New
                    </Button>
                  )}
                </Space>
              </Col>
            </Row>

            <Table
              loading={loading}
              columns={getColumns()}
              dataSource={data}
              rowKey={(record) => record.subject_id || record.class_id || record.user_id}
              pagination={{
                current: pagination.current,
                pageSize: pagination.pageSize,
                total: total,
                onChange: (page, pageSize) => setPagination({ current: page, pageSize })
              }}
            />
          </div>
        </Content>
      </Layout>

      <Modal
        title={editingKey ? "Update Information" : "Add New"}
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => { setIsModalOpen(false); form.resetFields(); }}
        okText="Save"
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreateOrUpdate}>
          {selectedKey === '1' && (
            <>
              <Form.Item name="subject_code" label="Subject Code" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="subject_name" label="Subject Name" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="dept_id" label="Dept ID" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
            </>
          )}
          {selectedKey === '2' && (
            <>
              <Form.Item name="class_code" label="Class Code" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="semester_id" label="Semester ID" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="subject_id" label="Subject ID" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="lecturer_id" label="Lecturer ID (UUID)" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </Layout>
  );
};

export default AdminDashboard;