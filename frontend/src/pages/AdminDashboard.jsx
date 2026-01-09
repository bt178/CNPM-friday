import React, { useState, useEffect } from 'react';
import {
  Layout, Typography, Button, Table, Avatar, Space, Badge,
  Input, Row, Col, Tooltip, Modal, Form, InputNumber, Select, message, Menu, Tabs
} from 'antd';
import {
  SearchOutlined, UserOutlined, BookOutlined, TeamOutlined,
  EditOutlined, DeleteOutlined, PlusOutlined,
  MenuOutlined, ArrowLeftOutlined, SettingOutlined, BellOutlined
} from '@ant-design/icons';

// Import services
import { subjectService, classService, userService } from '../services/api';

const { Title, Text } = Typography;
const { Header, Sider, Content } = Layout;

const AdminDashboard = () => {
  const [form] = Form.useForm();
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('1'); // 1: Subjects, 2: Semester, 3: Users

  // Data States
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  // Query States
  const [searchText, setSearchText] = useState('');
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });

  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingKey, setEditingKey] = useState(null);

  // --- FETCH DATA ---
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

      // Check format
      const resultData = Array.isArray(res.data) ? res.data : [];
      setData(resultData);

      // Since backend doesn't return total count yet, we pseudo-paginate or assume simplistic
      // For real pagination, backend response should include total.
      // Current implementation returns full list or limit list. 
      // We will assume data length is total for this simplified version unless backend supports count.
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

  // --- ACTIONS ---
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
          // Users typically soft de-activated, implementation pending

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
      // User create usually involves more logic (password), keeping simple for now

      message.success(editingKey ? 'Updated successfully' : 'Created successfully');
      setIsModalOpen(false);
      fetchData();
    } catch (err) {
      message.error(err.message || "Error: Please check input info.");
    }
  };

  // --- COLUMNS ---
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

    if (selectedKey === '1') { // SUBJECTS
      return [
        { title: 'Course Code', dataIndex: 'subject_code', key: 'subject_code' },
        { title: 'Subject Name', dataIndex: 'subject_name', key: 'subject_name' },
        { title: 'Dept ID', dataIndex: 'dept_id', key: 'dept_id', align: 'center' },
        commonActions
      ];
    } else if (selectedKey === '2') { // CLASSES
      return [
        { title: 'Class Code', dataIndex: 'class_code', key: 'class_code' },
        { title: 'Subject', dataIndex: 'subject_name', key: 'subject_name' },
        { title: 'Lecturer', dataIndex: 'lecturer_name', key: 'lecturer_name' },
        commonActions
      ];
    } else if (selectedKey === '3') { // USERS
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
            <Badge count={5}><BellOutlined style={{ fontSize: 18 }} /></Badge>
            <Space>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
              <Text strong>Administrator</Text>
            </Space>
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