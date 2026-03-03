?// src/components/common/Alert.jsx
// Componente Alert para mensagens

const Alert = ({ type = 'info', message, onClose, dismissible = true }) => {
  const types = {
    info: 'bg-blue-100 border-blue-400 text-blue-700',
    success: 'bg-green-100 border-green-400 text-green-700',
    warning: 'bg-yellow-100 border-yellow-400 text-yellow-700',
    error: 'bg-red-100 border-red-400 text-red-700'
  };

  return (
    <div className={`border-l-4 p-4 rounded ${types[type]}`} role="alert">
      <div className="flex justify-between items-center">
        <p>{message}</p>
        {dismissible && (
          <button
            onClick={onClose}
            className="ml-4 text-xl font-bold hover:opacity-70"
          >
            &times;
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
