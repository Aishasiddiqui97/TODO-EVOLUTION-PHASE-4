'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TodosPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [newTask, setNewTask] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Load tasks from localStorage
    if (typeof window !== 'undefined') {
      const savedTasks = localStorage.getItem('todo_tasks');
      setTasks(savedTasks ? JSON.parse(savedTasks) : []);
    }
  }, []);

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    const newTaskObj = {
      id: Date.now().toString(),
      description: newTask,
      completed: false,
      created_at: new Date().toISOString(),
    };
    const updatedTasks = [...tasks, newTaskObj];
    setTasks(updatedTasks);
    if (typeof window !== 'undefined') localStorage.setItem('todo_tasks', JSON.stringify(updatedTasks));
    setNewTask('');
    setShowAddModal(false);
  };

  const handleToggleComplete = (taskId: string) => {
    const updatedTasks = tasks.map(t =>
      t.id === taskId ? { ...t, completed: !t.completed } : t
    );
    setTasks(updatedTasks);
    if (typeof window !== 'undefined') localStorage.setItem('todo_tasks', JSON.stringify(updatedTasks));
  };

  const handleDeleteTask = (taskId: string) => {
    const updatedTasks = tasks.filter(t => t.id !== taskId);
    setTasks(updatedTasks);
    if (typeof window !== 'undefined') localStorage.setItem('todo_tasks', JSON.stringify(updatedTasks));
  };

  const handleLogout = () => {
    if (typeof window !== 'undefined') localStorage.removeItem('access_token');
    router.push('/');
  };

  const completedTasks = tasks.filter(t => t.completed);
  const pendingTasks = tasks.filter(t => !t.completed);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #0a0a0a 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      color: '#ffffff'
    }}>
      {/* Top Navigation Bar */}
      <nav style={{
        background: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 245, 255, 0.3)',
        padding: '20px 40px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '900',
            background: 'linear-gradient(90deg, #00f5ff 0%, #a855f7 50%, #ff006e 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            margin: 0
          }}>
            LOGIN DASHBOARD TEST
          </h1>
          <p style={{ fontSize: '12px', color: '#888', margin: '5px 0 0 0' }}>
            Evolution of Todo - Neon Edition
          </p>
        </div>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <a href="/chat" style={{ textDecoration: 'none' }}>
            <button
              style={{
                padding: '10px 25px',
                background: 'linear-gradient(90deg, #00f5ff, #a855f7)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 0 20px rgba(0, 245, 255, 0.5)',
                transition: 'transform 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              🤖 AI Chat
            </button>
          </a>
          <button
            onClick={handleLogout}
            style={{
              padding: '10px 25px',
              background: 'linear-gradient(90deg, #ff006e, #ff8c00)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: '0 0 20px rgba(255, 0, 110, 0.5)',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            Logout
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div style={{ padding: '40px', maxWidth: '1400px', margin: '0 auto' }}>

        {/* Stats Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
          marginBottom: '40px'
        }}>
          <div style={{
            background: 'rgba(0, 245, 255, 0.1)',
            border: '2px solid #00f5ff',
            borderRadius: '15px',
            padding: '25px',
            boxShadow: '0 0 30px rgba(0, 245, 255, 0.3)'
          }}>
            <div style={{ fontSize: '40px', marginBottom: '10px' }}>✅</div>
            <div style={{ fontSize: '14px', color: '#888', marginBottom: '5px' }}>Completed</div>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#00f5ff' }}>
              {completedTasks.length}
            </div>
          </div>

          <div style={{
            background: 'rgba(168, 85, 247, 0.1)',
            border: '2px solid #a855f7',
            borderRadius: '15px',
            padding: '25px',
            boxShadow: '0 0 30px rgba(168, 85, 247, 0.3)'
          }}>
            <div style={{ fontSize: '40px', marginBottom: '10px' }}>⏳</div>
            <div style={{ fontSize: '14px', color: '#888', marginBottom: '5px' }}>Pending</div>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#a855f7' }}>
              {pendingTasks.length}
            </div>
          </div>

          <div style={{
            background: 'rgba(255, 0, 110, 0.1)',
            border: '2px solid #ff006e',
            borderRadius: '15px',
            padding: '25px',
            boxShadow: '0 0 30px rgba(255, 0, 110, 0.3)'
          }}>
            <div style={{ fontSize: '40px', marginBottom: '10px' }}>📝</div>
            <div style={{ fontSize: '14px', color: '#888', marginBottom: '5px' }}>Total Tasks</div>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#ff006e' }}>
              {tasks.length}
            </div>
          </div>
        </div>

        {/* Add Task Button */}
        <button
          onClick={() => setShowAddModal(true)}
          style={{
            padding: '15px 40px',
            background: 'linear-gradient(90deg, #00f5ff, #a855f7)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '12px',
            fontSize: '18px',
            fontWeight: 'bold',
            cursor: 'pointer',
            marginBottom: '30px',
            boxShadow: '0 0 20px rgba(0, 245, 255, 0.5)'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          ➕ Add New Task
        </button>

        {/* Tasks List */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '20px',
          padding: '30px'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: 'bold',
            marginBottom: '20px',
            color: '#00f5ff'
          }}>
            📋 Your Tasks
          </h2>

          {tasks.length === 0 ? (
            <p style={{ color: '#888', textAlign: 'center', padding: '40px' }}>
              No tasks yet. Click "Add New Task" to get started!
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {tasks.map((task) => (
                <div
                  key={task.id}
                  style={{
                    background: task.completed
                      ? 'rgba(0, 255, 0, 0.1)'
                      : 'rgba(255, 255, 255, 0.05)',
                    border: task.completed
                      ? '1px solid rgba(0, 255, 0, 0.3)'
                      : '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '12px',
                    padding: '20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', flex: 1 }}>
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => handleToggleComplete(task.id)}
                      style={{
                        width: '24px',
                        height: '24px',
                        cursor: 'pointer'
                      }}
                    />
                    <span style={{
                      fontSize: '18px',
                      textDecoration: task.completed ? 'line-through' : 'none',
                      color: task.completed ? '#888' : '#ffffff'
                    }}>
                      {task.description}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteTask(task.id)}
                    style={{
                      padding: '8px 16px',
                      background: 'rgba(255, 0, 0, 0.2)',
                      border: '1px solid rgba(255, 0, 0, 0.5)',
                      borderRadius: '8px',
                      color: '#ff4444',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 0, 0, 0.3)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 0, 0, 0.2)'}
                  >
                    🗑️ Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Add Task Modal */}
      {showAddModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowAddModal(false)}
        >
          <div
            style={{
              background: 'rgba(10, 10, 10, 0.95)',
              border: '2px solid #00f5ff',
              borderRadius: '20px',
              padding: '40px',
              maxWidth: '500px',
              width: '90%',
              boxShadow: '0 0 50px rgba(0, 245, 255, 0.5)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{
              fontSize: '28px',
              fontWeight: 'bold',
              marginBottom: '25px',
              background: 'linear-gradient(90deg, #00f5ff, #a855f7)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              ✨ Add New Task
            </h3>
            <form onSubmit={handleAddTask}>
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="What needs to be done?"
                style={{
                  width: '100%',
                  padding: '15px',
                  fontSize: '16px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '10px',
                  color: '#ffffff',
                  marginBottom: '20px',
                  outline: 'none'
                }}
                autoFocus
              />
              <div style={{ display: 'flex', gap: '15px' }}>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    padding: '15px',
                    background: 'linear-gradient(90deg, #00f5ff, #a855f7)',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '10px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  Add Task
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{
                    padding: '15px 30px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: '#ffffff',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: '10px',
                    fontSize: '16px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
