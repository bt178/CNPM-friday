import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs'; // Cài đặt: npm install dayjs 
import { Layout, Typography, Button, Table, Avatar, Space, Badge, Calendar, Input, Select, Card, Tag, Row, Col, List, message, Modal } from 'antd';
import {
  SettingOutlined, BellOutlined, SearchOutlined, FilterOutlined,
  DashboardOutlined, TeamOutlined, DesktopOutlined, TableOutlined,
  FileTextOutlined, VideoCameraOutlined, SendOutlined, FormOutlined,
  LogoutOutlined, UserOutlined, AppstoreOutlined, ProjectOutlined,
  MenuOutlined, DownOutlined,
  LeftOutlined, RightOutlined
} from '@ant-design/icons';
import { Dropdown, Menu } from 'antd';

import { subjectService, projectService } from '../services/api';

const { Title, Text } = Typography;
const { Header, Sider, Content } = Layout;

const ProjectListView = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState({ name: '(Name)' });
  const [collapsed, setCollapsed] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(localStorage.getItem('user_avatar'));
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentDate, setCurrentDate] = useState(dayjs());
  const [searchText, setSearchText] = useState('');

  // Data State
  const [allData, setAllData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedData = localStorage.getItem('user_profile');
    if (savedData) setUserData(JSON.parse(savedData));

    // Fetch Projects
    const fetchProjects = async () => {
      setLoading(true);
      try {
        const res = await projectService.getAll();
        // Duplicate data to match original 16 items behavior if desired, or just use res.data
        // The original code did [...initialData, ...initialData]
        const fetchedData = res.data || [];
        setAllData(fetchedData);
      } catch (error) {
        console.error("Failed to fetch projects", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const handleChooseProject = async (record) => {
    try {
      if (record.status === 'Claimed') {
        message.warning('This project is already claimed!');
        return;
      }

      await projectService.update(record.key, { status: 'Claimed' });
      message.success('Project claimed successfully!');

      // Update local state
      setAllData(prev => prev.map(item =>
        item.key === record.key ? { ...item, status: 'Claimed' } : item
      ));
    } catch (error) {
      console.error(error);
      message.error('Failed to claim project');
    }
  };
  const handleLogout = () => {
    Modal.confirm({
      title: 'Xác nhận đăng xuất',
      content: 'Bạn có chắc chắn muốn thoát khỏi hệ thống không?',
      okText: 'Đăng xuất',
      cancelText: 'Hủy',
      onOk: () => {
        // Gọi service xóa dữ liệu
        localStorage.removeItem('user_profile');
        localStorage.removeItem('user_avatar');

        message.success('Đã đăng xuất thành công');

        // Chuyển hướng về trang Login
        navigate('/login');
      },
    });
  };

  // Logic xử lý Lịch
  const startDay = currentDate.startOf('month').day();
  const daysInMonth = currentDate.daysInMonth();
  const daysArray = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const emptyDays = Array.from({ length: startDay }, (_, i) => i);

  const nextMonth = () => setCurrentDate(currentDate.add(1, 'month'));
  const prevMonth = () => setCurrentDate(currentDate.subtract(1, 'month'));

  const categories = [...new Set(allData.map(item => item.category))];

  // Logic tìm kiếm & lọc kết hợp
  const sortedDataSource = allData
    .filter(item => {
      const searchKey = searchText.trim().toLowerCase();
      const matchesCategory = selectedCategory ? item.category === selectedCategory : true;
      const matchesSearch = item.topic.toLowerCase().includes(searchKey);
      return matchesCategory && matchesSearch;
    })
    .sort((a, b) => {
      // Ưu tiên "Claimed" status
      if (a.status === 'Claimed' && b.status !== 'Claimed') return 1;
      if (a.status !== 'Claimed' && b.status === 'Claimed') return -1;
      // Sort bằng topic
      return a.topic.localeCompare(b.topic);
    });

  const handleMenuClick = (e) => {
    if (e.key === 'all') {
      setSelectedCategory(null);
    } else {
      setSelectedCategory(e.key);
    }
  };

  const menu = (
    <Menu onClick={handleMenuClick}>
      <Menu.Item key="all">All Categories</Menu.Item>
      {categories.map(cat => (
        <Menu.Item key={cat}>{cat}</Menu.Item>
      ))}
    </Menu>
  );

  const columns = [
    { title: 'Proposer', dataIndex: 'proposer', key: 'proposer', width: 120 },
    { title: 'Topic title', dataIndex: 'topic', key: 'topic' },
    { title: 'Category', dataIndex: 'category', key: 'category', width: 100 },
    { title: 'Date started', dataIndex: 'date', key: 'date', width: 120 },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 100 },
    {
      title: 'Activity',
      key: 'activity',
      width: 100,
      render: (_, record) => (
        <Button
          size="small"
          type="default"
          style={{
            background: record.status === 'Claimed' ? '#d9d9d9' : '#1890ff',
            color: record.status === 'Claimed' ? '#00000040' : '#fff',
            border: 'none',
            cursor: record.status === 'Claimed' ? 'not-allowed' : 'pointer'
          }}
          onClick={() => handleChooseProject(record)}
          disabled={record.status === 'Claimed'}
        >
          {record.status === 'Claimed' ? 'Claimed' : 'Choose'}
        </Button>
      )
    },
  ];

  const recentActivities = [
    'Smart Inventory System', 'AI Health Monitor', 'Smart Campus App', 'Drone Delivery'
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#fff' }}>
      {/* Top Header */}
      <Header style={{
        background: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        padding: '0 24px',
        borderBottom: '1px solid #f0f0f0',
        height: '64px',
        lineHeight: '64px',
      }}>
        <Space size="large">
          <Avatar size="small" style={{ backgroundColor: '#ccc' }}>logo</Avatar>
          <Text strong style={{ fontSize: '16px' }}>Name of web</Text>
        </Space>
        <Badge dot offset={[-5, 5]}>
          <BellOutlined style={{ fontSize: 20, color: '#000' }} />
        </Badge>
      </Header>

      <Layout>
        {/* Thanh Menu bên trái (Sidebar) */}
        <Sider
          width={260}
          theme="light"
          style={{ borderRight: '1px solid #f0f0f0' }}
          collapsible
          collapsed={collapsed}
          trigger={null}
        >
          <div style={{ padding: collapsed ? '24px 8px' : '24px 24px 0', transition: 'all 0.2s', display: 'flex', flexDirection: 'column', height: '100%' }}>

            <div style={{ marginBottom: 24, paddingLeft: collapsed ? 12 : 0, transition: 'all 0.2s' }}>
              <Button
                type="text"
                icon={<MenuOutlined style={{ fontSize: '18px' }} />}
                onClick={() => setCollapsed(!collapsed)}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32, justifyContent: collapsed ? 'center' : 'flex-start', flexDirection: collapsed ? 'column' : 'row' }}>
              <Avatar size={collapsed ? 40 : 64} src={avatarUrl} style={{ backgroundColor: '#d9d9d9', marginRight: collapsed ? 0 : 16, transition: 'all 0.2s' }} />
              {!collapsed && (
                <div>
                  <Title level={4} style={{ margin: 0, fontWeight: 'normal', whiteSpace: 'nowrap' }}>Hi <span style={{ color: '#1890ff' }}>{userData.name.split(' ').pop()}</span>!</Title>
                </div>
              )}
            </div>




            <div style={{ marginBottom: 24 }}>
              {!collapsed && <Text strong style={{ color: '#1890ff', fontSize: '12px', letterSpacing: '1px' }}>OVERVIEW</Text>}
              {collapsed && <div style={{ height: 20 }} />}

              <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size={8}>
                <Button type="text" block icon={<DashboardOutlined />} style={{ textAlign: collapsed ? 'center' : 'left', color: '#81bef6ff' }}>
                  {!collapsed && "Dashboard"}
                </Button>
                <Button type="text" block icon={<TeamOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Team Management"}
                </Button>
                <Button type="text" block icon={<DesktopOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Real-time Workspace"}
                </Button>
                <Button type="text" block icon={<TableOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Kanban Board Detail"}
                </Button>
                <Button type="text" block icon={<FormOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Whiteboard Canvas"}
                </Button>
                <Button type="text" block icon={<VideoCameraOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Video Meeting Room"}
                </Button>
                <Button type="text" block icon={<SendOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Submission Portal"}
                </Button>
                <Button type="text" block icon={<FileTextOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }}>
                  {!collapsed && "Peer Review Form"}
                </Button>
              </Space>
            </div>

            <div style={{ flex: 1 }} />

            <div>
              {!collapsed && <Text strong style={{ color: '#1890ff', fontSize: '12px', letterSpacing: '1px' }}>SETTINGS</Text>}
              {collapsed && <div style={{ height: 20 }} />}
              <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size={8}>
                <Button type="text" block icon={<SettingOutlined />} style={{ textAlign: collapsed ? 'center' : 'left' }} onClick={() => navigate('/profile')}>
                  {!collapsed && "Settings"}
                </Button>

                <Button
                  type="text"
                  block
                  danger // Thêm màu đỏ để cảnh báo
                  icon={<LogoutOutlined />}
                  style={{ textAlign: collapsed ? 'center' : 'left' }}
                  onClick={handleLogout}
                >
                  {!collapsed && "Logout"}
                </Button>
              </Space>
            </div>

            <div style={{ flex: 1 }} />
          </div>
        </Sider>

        {/* nội dung chính */}
        <Content style={{ padding: '24px 32px', background: '#fff' }}>
          <div style={{ marginBottom: 120 }}>
            <Title level={2} style={{ margin: '0 0 8px 0', fontWeight: 'normal' }}>Project List View</Title>
            <Text style={{ fontSize: '16px' }}>List of topics for students to choose</Text>
          </div>

          {/* Tìm kiếm và Lọc */}
          <Row justify="end" gutter={16} style={{ marginBottom: 16 }}>
            <Col>
              <Input
                placeholder="Quick search topic title..."
                prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
                style={{
                  width: 300,
                  borderRadius: 8,
                  height: '40px',
                  background: '#f0f2f5',
                  border: 'none'
                }}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
              />
            </Col>
            <Col>
              <Dropdown overlay={menu} trigger={['click']}>
                <Button style={{ background: '#d9d9d9', border: 'none', borderRadius: 6 }}>
                  {selectedCategory ? selectedCategory : 'Sort by category'} <DownOutlined />
                </Button>
              </Dropdown>
            </Col>
          </Row>

          {/* Bảng dữ liệu với tính năng cuộn trang */}
          <Table
            loading={loading}
            dataSource={sortedDataSource}
            columns={columns}
            pagination={false}
            scroll={{ y: 450 }}
            rowClassName={(record, index) => index % 2 === 0 ? 'table-row-light' : 'table-row-light'}
            style={{
              border: 'none',
            }}
            onRow={() => ({
              style: { background: '#d9d9d9', marginBottom: '4px' }
            })}
          />
          <style>{`
                .ant-table-thead > tr > th {
                    background: #4a90e2 !important; /* Xanh dương đậm hơn */
                    color: white !important;        /* Chữ trắng mới nổi trên nền xanh */
                    font-weight: 600;
                    border-right: 2px solid white !important;
                }
                .ant-table-tbody > tr > td {
                    background: #e6e6e6;
                    border-bottom: 2px solid white !important; /* Visual gap */
                    border-right: 2px solid white !important; /* Vertical Separator */
                }
                .ant-table-container {
                    background: transparent;
                }
            `}</style>
        </Content>

        {/* Thanh Menu bên phải (Sidebar) */}
        <Sider width={300} theme="light" style={{ padding: '24px', borderLeft: '1px solid #f0f0f0' }}>
          <div style={{ background: '#fff', borderRadius: 12, marginBottom: 40 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text strong style={{ fontSize: '16px' }}>{currentDate.format('MMMM YYYY')}</Text>
              <Space>
                <Button size="small" icon={<LeftOutlined />} onClick={prevMonth} />
                <Button size="small" icon={<RightOutlined />} onClick={nextMonth} />
              </Space>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', textAlign: 'center' }}>
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                <Text key={day} type="secondary" style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 8 }}>{day}</Text>
              ))}

              {/* Ô trống của tháng trước */}
              {emptyDays.map(i => <div key={`empty-${i}`} />)}

              {/* Các ngày trong tháng */}
              {daysArray.map(day => {
                const isToday = day === dayjs().date() && currentDate.isSame(dayjs(), 'month');
                return (
                  <div key={day} style={{
                    padding: '8px 0',
                    cursor: 'pointer',
                    borderRadius: '50%',
                    background: isToday ? '#1890ff' : 'transparent',
                    color: isToday ? '#fff' : 'inherit',
                    fontWeight: isToday ? 'bold' : 'normal',
                    transition: '0.3s'
                  }}>
                    {day}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Activities */}
          <Title level={5}>Recent activities</Title>
          <div style={{ background: '#d9d9d9', borderRadius: 12, padding: '16px', minHeight: 150 }}>
            <List
              dataSource={recentActivities}
              renderItem={item => (
                <List.Item style={{ padding: '4px 0', border: 'none' }}>
                  <Typography.Text>{item}</Typography.Text>
                </List.Item>
              )}
            />
          </div>
          <div style={{ textAlign: 'right', marginTop: 8 }}>
            <Text style={{ fontSize: 12, cursor: 'pointer' }}>see more</Text>
          </div>
        </Sider>
      </Layout>
    </Layout>
  );
};

export default ProjectListView;