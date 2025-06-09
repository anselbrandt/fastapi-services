import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

type Data = {
  status: {
    db: string;
  };
};

function App() {
  const [status, setStatus] = useState<Data>();

  useEffect(() => {
    async function getStatus() {
      const response = await fetch(`${API_URL}/health`);
      const data = (await response.json()) as Data;
      if ("status" in data && "db" in data.status) {
        setStatus(data as Data);
      }
    }
    getStatus();
  }, []);
  return (
    <>
      <div className="h-screen flex flex-col items-center justify-center">
        <div className="text-4xl font-bold space-y-4 text-center">
          <h1 className="text-sky-500">Docker</h1>
          <h1 className="text-teal-500">FastAPI + PostgreSQL</h1>
          <h1 className="text-cyan-500">Vite + React</h1>
        </div>
        <div className="">
          <pre>{JSON.stringify(status, null, 2)}</pre>
        </div>
      </div>
    </>
  );
}

export default App;
