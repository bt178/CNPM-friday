import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs'; // Cài đặt: npm install dayjs 
import { Layout, Typography, Button, Table, Avatar, Space, Badge, Calendar, Input, Select, Card, Tag, Row, Col, List, message, Modal, Popover, Divider } from 'antd';
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
import { useAuth, resolveRoleName } from '../components/AuthContext';

const { Title, Text } = Typography;
const { Header, Sider, Content } = Layout;

import './DashboardPage.css';

const ProjectListView = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [userData, setUserData] = useState(() => ({
    name: user?.full_name || user?.email || '(Name)'
  }));
  const [collapsed, setCollapsed] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(localStorage.getItem('user_avatar'));
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentDate, setCurrentDate] = useState(dayjs());
  const [searchText, setSearchText] = useState('');

  // Data State
  const [allData, setAllData] = useState([]);
  const [loading, setLoading] = useState(true);

  const canUseStorage = () => typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';

  const readStoredUser = () => {
    if (!canUseStorage()) return null;
    const raw = window.localStorage.getItem('user');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (_err) {
      return null;
    }
  };

  const buildScopedKey = (baseKey, user) => {
    const identifier = user?.user_id || user?.email || user?.id;
    return identifier ? `${baseKey}_${identifier}` : null;
  };

  const readActiveProjects = () => {
    if (!canUseStorage()) return [];
    const storedUser = readStoredUser();
    const scopedKey = buildScopedKey('active_projects', storedUser || user);
    const scopedRaw = scopedKey && window.localStorage.getItem(scopedKey);
    const raw = scopedRaw || window.localStorage.getItem('active_projects');
    if (!raw) return [];
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed;
      }
      if (parsed && Array.isArray(parsed.items)) {
        if (!scopedRaw && parsed._owner && storedUser?.email && parsed._owner !== storedUser.email) {
          return [];
        }
        return parsed.items;
      }
      return [];
    } catch (_err) {
      return [];
    }
  };

  const writeActiveProjects = (items) => {
    if (!canUseStorage()) return;
    const payload = { _owner: user?.email || null, items };
    const scopedKey = buildScopedKey('active_projects', user);
    if (scopedKey) {
      window.localStorage.setItem(scopedKey, JSON.stringify(payload));
    }
    window.localStorage.setItem('active_projects', JSON.stringify(payload));
    window.dispatchEvent(new CustomEvent('active-projects-updated', { detail: { items } }));
  };

  const readStoredProfile = () => {
    if (!canUseStorage()) return null;
    const storedUser = readStoredUser();
    const scopedKey = buildScopedKey('user_profile', storedUser);
    const scopedRaw = scopedKey && window.localStorage.getItem(scopedKey);
    const raw = scopedRaw || window.localStorage.getItem('user_profile');
    if (!raw) return null;
    try {
      const parsed = JSON.parse(raw);
      if (!scopedRaw && parsed?._owner && storedUser?.email && parsed._owner !== storedUser.email) {
        return null;
      }
      return parsed;
    } catch (_err) {
      return null;
    }
  };

  const readStoredAvatar = () => {
    if (!canUseStorage()) return null;
    const storedUser = readStoredUser();
    const scopedKey = buildScopedKey('user_avatar', storedUser);
    return (scopedKey && window.localStorage.getItem(scopedKey)) || window.localStorage.getItem('user_avatar');
  };

  const syncProfileFromStorage = () => {
    const savedProfile = readStoredProfile();
    if (savedProfile) {
      setUserData((prev) => ({ ...prev, ...savedProfile }));
    }
    const savedAvatar = readStoredAvatar();
    if (savedAvatar !== null && savedAvatar !== undefined) {
      setAvatarUrl(savedAvatar);
    }
  };

  useEffect(() => {
    syncProfileFromStorage();

    const handleProfileUpdated = () => syncProfileFromStorage();
    const handleAvatarUpdated = () => syncProfileFromStorage();
    const handleStorage = (event) => {
      if (event.key?.startsWith('user_profile') || event.key?.startsWith('user_avatar') || event.key === 'user') {
        syncProfileFromStorage();
      }
    };

    window.addEventListener('profile-updated', handleProfileUpdated);
    window.addEventListener('avatar-updated', handleAvatarUpdated);
    window.addEventListener('storage', handleStorage);

    return () => {
      window.removeEventListener('profile-updated', handleProfileUpdated);
      window.removeEventListener('avatar-updated', handleAvatarUpdated);
      window.removeEventListener('storage', handleStorage);
    };
  }, []);

  useEffect(() => {
    if (!user) {
      return;
    }
    setUserData((prev) => ({
      ...prev,
      name: user.full_name || user.email || prev.name
    }));
  }, [user]);

  useEffect(() => {

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

      const activeItems = readActiveProjects();
      const nextItem = {
        id: record.key,
        title: record.topic || record.title || 'Untitled Project',
        description: `${record.category || 'Project'} • ${record.date || 'N/A'}`,
        iconType: 'project',
      };
      const nextItems = activeItems.some((item) => String(item.id) === String(nextItem.id))
        ? activeItems
        : [nextItem, ...activeItems];
      writeActiveProjects(nextItems);

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
        logout();
      },
    });
  };

  const [isNotificationOpen, setNotificationOpen] = useState(false);
  const notificationAnchorRef = useRef(null);

  const notifications = useMemo(() => ([
    {
      id: 1,
      title: 'New Task Assigned',
      description: 'You have been assigned a new task titled "Complete Project Report."',
      timeAgo: '10 minutes ago',
    },
    {
      id: 2,
      title: 'Deadline Warning',
      description: "Reminder: The deadline for the task 'Submit Proposal' is approaching.",
      timeAgo: '10 minutes ago',
    },
    {
      id: 3,
      title: 'New Message Received',
      description: 'You have a new message from Test user.',
      timeAgo: '10 minutes ago',
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

  const [hoveredNav, setHoveredNav] = useState(null);

  const navButtonStyles = (key, { active, danger } = {}) => ({
    textAlign: collapsed ? 'center' : 'left',
    display: 'flex',
    alignItems: 'center',
    justifyContent: collapsed ? 'center' : 'flex-start',
    borderRadius: 8,
    padding: collapsed ? '8px 0' : '8px 12px',
    color: danger ? '#d4380d' : active ? '#1890ff' : '#595959',
    fontWeight: active ? 600 : 500,
    backgroundColor: hoveredNav === key ? 'rgba(24, 144, 255, 0.08)' : 'transparent',
    transform: hoveredNav === key && !collapsed ? 'translateX(2px)' : 'none',
    transition: 'all 0.2s ease',
  });

  const navButtonInteractions = (key, options) => ({
    style: navButtonStyles(key, options),
    onMouseEnter: () => setHoveredNav(key),
    onMouseLeave: () => setHoveredNav(null),
  });

  const hamburgerLineBase = {
    width: 18,
    height: 2,
    backgroundColor: '#262626',
    display: 'block',
    borderRadius: 2,
    transition: 'transform 0.3s ease, opacity 0.3s ease',
  };

  const hamburgerLineStyle = (position) => {
    if (collapsed) {
      switch (position) {
        case 'top':
          return { ...hamburgerLineBase, transform: 'translateY(0) rotate(0)' };
        case 'middle':
          return { ...hamburgerLineBase, opacity: 1 };
        case 'bottom':
        default:
          return { ...hamburgerLineBase, transform: 'translateY(0) rotate(0)' };
      }
    }
    switch (position) {
      case 'top':
        return { ...hamburgerLineBase, transform: 'translateY(6px) rotate(45deg)' };
      case 'middle':
        return { ...hamburgerLineBase, opacity: 0 };
      case 'bottom':
      default:
        return { ...hamburgerLineBase, transform: 'translateY(-6px) rotate(-45deg)' };
    }
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
    <Layout className="dashboard-layout" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Top Header */}
      <Header className="dashboard-header" style={{
        position: 'fixed',
        top: 0,
        zIndex: 1000,
        width: '100%',
        background: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        padding: '0 24px',
        borderBottom: '1px solid #f0f0f0',
        height: '64px',
        lineHeight: '64px',
      }}>
        <Space size="large">
          <Avatar size="small" style={{ backgroundColor: '#1890ff' }}>C</Avatar>
          <Text strong style={{ fontSize: '16px' }}>CollabSphere</Text>
        </Space>
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
                <BellOutlined style={{ fontSize: 20, color: '#000', cursor: 'pointer' }} />
              </Badge>
            </Popover>
          </div>
          <Input
            placeholder="Search..."
            prefix={<SearchOutlined />}
            style={{ width: 200, borderRadius: '6px' }}
          />
        </Space>
      </Header>

      <Layout style={{ marginTop: '64px', height: 'calc(100vh - 64px)', background: '#f5f5f5' }}>
        {/* Thanh Menu bên trái (Sidebar) */}
        <Sider
          className="dashboard-sider"
          width={240}
          theme="light"
          style={{
            borderRight: '1px solid #f0f0f0',
            height: 'calc(100vh - 64px)',
            overflow: 'hidden',
            position: 'fixed',
            left: 0,
            top: '64px',
            background: '#ffffff',
            boxShadow: '6px 0 18px rgba(15, 18, 21, 0.04)'
          }}
          collapsible
          collapsed={collapsed}
          trigger={null}
        >
          <div style={{ padding: collapsed ? '24px 8px' : '24px 24px 0', display: 'flex', flexDirection: 'column', height: '100%' }}>

            <div style={{ marginBottom: 24, paddingLeft: collapsed ? 12 : 0 }}>
              <button
                type="button"
                onClick={() => setCollapsed(!collapsed)}
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                style={{
                  border: '1px solid #f0f0f0',
                  borderRadius: 12,
                  width: 40,
                  height: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  background: '#fff',
                  transition: 'box-shadow 0.3s ease',
                }}
                onMouseEnter={(event) => {
                  event.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.08)';
                }}
                onMouseLeave={(event) => {
                  event.currentTarget.style.boxShadow = 'none';
                }}
              >
                <span style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <span style={hamburgerLineStyle('top')} />
                  <span style={hamburgerLineStyle('middle')} />
                  <span style={hamburgerLineStyle('bottom')} />
                </span>
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32, justifyContent: collapsed ? 'center' : 'flex-start', flexDirection: collapsed ? 'column' : 'row' }}>
              <Avatar size={collapsed ? 40 : 64} src={avatarUrl} style={{ backgroundColor: '#d9d9d9', marginRight: collapsed ? 0 : 16 }} />
              {!collapsed && (
                <div>
                  <Title level={4} style={{ margin: 0, fontWeight: 'normal', whiteSpace: 'nowrap' }}>Hi <span style={{ color: '#1890ff' }}>{userData.name.split(' ').pop()}</span>!</Title>
                  <Text type="secondary">
                    {(resolveRoleName(user) || 'Student')
                      .split('_')
                      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                      .join(' ')}
                  </Text>
                </div>
              )}
            </div>

            <div style={{ marginBottom: 16 }}>
              {!collapsed && <Text strong style={{ color: '#1890ff', fontSize: '12px', letterSpacing: '1px' }}>OVERVIEW</Text>}
              <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size={8}>
                <Button
                  type="text"
                  block
                  icon={<DashboardOutlined />}
                  onClick={() => navigate('/dashboard')}
                  {...navButtonInteractions('dashboard')}
                >
                  {!collapsed && "Dashboard"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<TeamOutlined />}
                  {...navButtonInteractions('team')}
                >
                  {!collapsed && "Team Management"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<DesktopOutlined />}
                  {...navButtonInteractions('workspace')}
                >
                  {!collapsed && "Real-time Workspace"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<TableOutlined />}
                  {...navButtonInteractions('kanban')}
                >
                  {!collapsed && "Kanban Board Detail"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<FormOutlined />}
                  {...navButtonInteractions('whiteboard')}
                >
                  {!collapsed && "Whiteboard Canvas"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<VideoCameraOutlined />}
                  {...navButtonInteractions('video')}
                >
                  {!collapsed && "Video Meeting Room"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<SendOutlined />}
                  {...navButtonInteractions('submission')}
                >
                  {!collapsed && "Submission Portal"}
                </Button>
                <Button
                  type="text"
                  block
                  icon={<FileTextOutlined />}
                  {...navButtonInteractions('peer')}
                >
                  {!collapsed && "Peer Review Form"}
                </Button>
              </Space>
            </div>

            <div style={{ height: collapsed ? 12 : 200 }} />

            <div>
              {!collapsed && <Text strong style={{ color: '#1890ff', fontSize: '12px', letterSpacing: '1px' }}>SETTINGS</Text>}
              <Space direction="vertical" style={{ width: '100%', marginTop: 16 }} size={8}>
                <Button
                  type="text"
                  block
                  icon={<SettingOutlined />}
                  onClick={() => navigate('/profile')}
                  {...navButtonInteractions('settings')}
                >
                  {!collapsed && "Settings"}
                </Button>

                <Button
                  type="text"
                  block
                  icon={<LogoutOutlined />}
                  onClick={handleLogout}
                  {...navButtonInteractions('logout', { danger: true })}
                >
                  {!collapsed && "Logout"}
                </Button>
              </Space>
            </div>
          </div>
        </Sider>

        {/* nội dung chính */}
        <Content className="dashboard-content" style={{
          marginLeft: collapsed ? '80px' : '240px',
          marginRight: '300px',
          padding: '24px',
          background: '#f5f5f5',
          minHeight: 'calc(100vh - 64px)'
        }}>
          <div style={{ marginBottom: 24 }}>
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
                  background: '#fff',
                  border: '1px solid #d9d9d9'
                }}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
              />
            </Col>
            <Col>
              <Dropdown overlay={menu} trigger={['click']}>
                <Button style={{ background: '#fff', border: '1px solid #d9d9d9', borderRadius: 6, height: '40px' }}>
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
            scroll={{ y: 600 }}
            rowClassName={(record, index) => index % 2 === 0 ? 'table-row-light' : 'table-row-light'}
            style={{
              borderRadius: 8,
              overflow: 'hidden',
              boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
            }}
          />
          <style>{`
                .ant-table-thead > tr > th {
                    background: #1890ff !important;
                    color: white !important;
                    font-weight: 600;
                }
            `}</style>
        </Content>

        {/* Thanh Menu bên phải (Sidebar) */}
        <Sider
          className="dashboard-sider dashboard-sider--right"
          width={300}
          theme="light"
          style={{
            position: 'fixed',
            right: 0,
            top: '64px',
            height: 'calc(100vh - 64px)',
            overflow: 'auto',
            borderLeft: '1px solid #f0f0f0',
            background: '#fff',
            padding: '24px'
          }}
        >
          {/* CALENDAR SECTION */}
          <div style={{
            background: '#fff',
            borderRadius: 12,
            padding: '16px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            marginBottom: 24
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text strong style={{ fontSize: '16px' }}>{currentDate.format('MMMM YYYY')}</Text>
              <Space>
                <Button size="small" type="text" icon={<LeftOutlined />} onClick={prevMonth} style={{ border: '1px solid #d9d9d9' }} />
                <Button size="small" type="text" icon={<RightOutlined />} onClick={nextMonth} style={{ border: '1px solid #d9d9d9' }} />
              </Space>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', textAlign: 'center', gap: '4px' }}>
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                <Text key={day} type="secondary" style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 4 }}>{day}</Text>
              ))}

              {emptyDays.map(i => <div key={`empty-${i}`} style={{ height: '32px' }} />)}

              {daysArray.map(day => {
                const isToday = day === dayjs().date() && currentDate.isSame(dayjs(), 'month');
                return (
                  <div
                    key={day}
                    className={`calendar-day${isToday ? ' calendar-day--today' : ''}`}
                  >
                    {day}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Activities */}
          <div style={{ marginBottom: 24 }}>
            <Title level={5} style={{ marginBottom: 12 }}>Recent activities</Title>
            <div style={{ background: '#f5f5f5', borderRadius: 12, padding: '16px', minHeight: 150 }}>
              <List
                dataSource={recentActivities}
                renderItem={item => (
                  <List.Item className="recent-activity-item">
                    <Typography.Text style={{ fontSize: '14px' }}>{item}</Typography.Text>
                  </List.Item>
                )}
              />
            </div>
            <div style={{ textAlign: 'right', marginTop: 8 }}>
              <Text className="recent-activity-cta">
                see more
              </Text>
            </div>
          </div>

          {/* Optional: Additional widget */}
          <div style={{
            background: '#f9f0ff',
            borderRadius: 12,
            padding: '16px',
            textAlign: 'center'
          }}>
            <Title level={5} style={{ color: '#722ed1' }}>Upcoming Events</Title>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              No events scheduled for today
            </Text>
          </div>
        </Sider>
      </Layout>
    </Layout>
  );
};

export default ProjectListView;