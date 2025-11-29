import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Bed, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Bell,
  Calendar,
  BarChart3
} from 'lucide-react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [surgePrediction, setSurgePrediction] = useState(null);
  const [bedOccupancy, setBedOccupancy] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [dashboard, prediction, beds] = await Promise.all([
        axios.get(`${API_BASE_URL}/analytics/dashboard/`),
        axios.get(`${API_BASE_URL}/surge/predict/?hours_ahead=24`),
        axios.get(`${API_BASE_URL}/beds/occupancy/`)
      ]);

      setDashboardData(dashboard.data);
      setSurgePrediction(prediction.data);
      setBedOccupancy(beds.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const handleNotifyStaff = async () => {
    try {
      await axios.post(`${API_BASE_URL}/staff/notify/`);
      alert('Staff notifications sent!');
    } catch (error) {
      console.error('Error sending notifications:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-16 h-16 text-blue-600 animate-pulse mx-auto mb-4" />
          <p className="text-xl text-gray-700">Loading SurgeSentinel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
              <Activity className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">SurgeSentinel</h1>
              <p className="text-sm text-gray-600">AI Hospital Surge Management</p>
            </div>
          </div>
          <button
            onClick={handleNotifyStaff}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <Bell className="w-4 h-4" />
            Notify Staff
          </button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-6 mt-6">
        <div className="bg-white rounded-lg shadow p-2 flex gap-2">
          {['overview', 'predictions', 'beds', 'recommendations'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'overview' && (
          <Overview 
            dashboardData={dashboardData} 
            surgePrediction={surgePrediction}
            bedOccupancy={bedOccupancy}
          />
        )}
        {activeTab === 'predictions' && (
          <Predictions surgePrediction={surgePrediction} />
        )}
        {activeTab === 'beds' && (
          <BedManagement bedOccupancy={bedOccupancy} />
        )}
        {activeTab === 'recommendations' && (
          <Recommendations surgePrediction={surgePrediction} />
        )}
      </main>
    </div>
  );
}

// Overview Tab Component
function Overview({ dashboardData, surgePrediction, bedOccupancy }) {
  const stats = [
    {
      icon: <Users className="w-8 h-8" />,
      label: 'Today\'s Admissions',
      value: dashboardData?.today_admissions || 0,
      color: 'blue'
    },
    {
      icon: <Bed className="w-8 h-8" />,
      label: 'Bed Occupancy',
      value: `${dashboardData?.occupancy_rate || 0}%`,
      color: 'green'
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      label: 'Predicted Surge',
      value: surgePrediction?.predicted_patients || 0,
      color: 'purple'
    },
    {
      icon: <Activity className="w-8 h-8" />,
      label: 'Confidence',
      value: `${Math.round((surgePrediction?.confidence || 0) * 100)}%`,
      color: 'orange'
    }
  ];

  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-xl shadow-lg p-6">
            <div className={`w-14 h-14 bg-gradient-to-br ${colorClasses[stat.color]} rounded-lg flex items-center justify-center text-white mb-4`}>
              {stat.icon}
            </div>
            <p className="text-gray-600 text-sm mb-1">{stat.label}</p>
            <p className="text-3xl font-bold text-gray-800">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <OccupancyChart bedOccupancy={bedOccupancy} />
        <SurgeAlertCard surgePrediction={surgePrediction} />
      </div>
    </div>
  );
}

// Occupancy Chart Component
function OccupancyChart({ bedOccupancy }) {
  const chartData = {
    labels: bedOccupancy.map(b => b.department),
    datasets: [
      {
        label: 'Occupied',
        data: bedOccupancy.map(b => b.occupied_beds),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
      {
        label: 'Available',
        data: bedOccupancy.map(b => b.available_beds),
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Bed Occupancy by Department'
      }
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="h-64">
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
}

// Surge Alert Card
function SurgeAlertCard({ surgePrediction }) {
  const predicted = surgePrediction?.predicted_patients || 0;
  const confidence = surgePrediction?.confidence || 0;

  let alertLevel = 'low';
  let alertColor = 'green';
  let alertIcon = <CheckCircle className="w-6 h-6" />;

  if (predicted > 50) {
    alertLevel = 'high';
    alertColor = 'red';
    alertIcon = <AlertTriangle className="w-6 h-6" />;
  } else if (predicted > 30) {
    alertLevel = 'medium';
    alertColor = 'yellow';
    alertIcon = <AlertTriangle className="w-6 h-6" />;
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 border-${alertColor}-500`}>
      <div className="flex items-center gap-3 mb-4">
        <div className={`text-${alertColor}-600`}>
          {alertIcon}
        </div>
        <h3 className="text-xl font-bold text-gray-800">Surge Alert</h3>
      </div>
      <p className="text-gray-600 mb-4">
        Predicted patient surge in next 24 hours
      </p>
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Expected Patients:</span>
          <span className="text-2xl font-bold text-gray-900">{predicted}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Confidence:</span>
          <span className="font-semibold text-gray-900">{Math.round(confidence * 100)}%</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Alert Level:</span>
          <span className={`font-semibold text-${alertColor}-600 uppercase`}>{alertLevel}</span>
        </div>
      </div>
    </div>
  );
}

// Predictions Tab
function Predictions({ surgePrediction }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Surge Prediction Details</h2>
      <div className="prose max-w-none">
        <p className="text-gray-700 mb-4">
          <strong>Reasoning:</strong> {surgePrediction?.reasoning || 'No prediction available'}
        </p>
        <div className="bg-blue-50 rounded-lg p-4 mt-4">
          <h3 className="font-semibold text-blue-900 mb-2">Key Factors</h3>
          <ul className="list-disc list-inside text-blue-800">
            <li>Historical patient flow patterns</li>
            <li>Environmental conditions (AQI, weather)</li>
            <li>Upcoming events and festivals</li>
            <li>Current bed occupancy trends</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Bed Management Tab
function BedManagement({ bedOccupancy }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Bed Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bedOccupancy.map((dept, index) => (
          <div key={index} className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">{dept.department}</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Beds:</span>
                <span className="font-semibold">{dept.total_beds}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Occupied:</span>
                <span className="font-semibold text-blue-600">{dept.occupied_beds}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Available:</span>
                <span className="font-semibold text-green-600">{dept.available_beds}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mt-2">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all"
                  style={{ width: `${dept.occupancy_rate}%` }}
                />
              </div>
              <p className="text-center text-sm text-gray-600">
                {dept.occupancy_rate.toFixed(1)}% Occupied
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Recommendations Tab
function Recommendations({ surgePrediction }) {
  const recommendations = surgePrediction?.recommendations || {};
  const actions = recommendations.actions || [];

  const priorityColors = {
    urgent: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'blue'
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">AI Recommendations</h2>
      <div className="grid gap-4">
        {actions.length > 0 ? (
          actions.map((action, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl shadow-lg p-6 border-l-4 border-${priorityColors[action.priority]}-500`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-${priorityColors[action.priority]}-100 text-${priorityColors[action.priority]}-800`}>
                    {action.priority.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-600">{action.category}</span>
                </div>
                <span className="text-sm text-gray-500">{action.timeline}</span>
              </div>
              <p className="text-lg font-semibold text-gray-800 mb-2">{action.action}</p>
              <p className="text-sm text-gray-600">Department: {action.department}</p>
            </div>
          ))
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-6 text-center">
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
            <p className="text-gray-700">No urgent recommendations at this time.</p>
            <p className="text-sm text-gray-500 mt-2">System is operating normally.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;