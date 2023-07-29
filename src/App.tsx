import React, { useState, useEffect } from "react";
import axios from "axios";
const App: React.FC = () => {
    const [ip, setIp] = useState<string>("");
    const [timeLeft, setTimeLeft] = useState<number>(0);
    const [timerStarted, setTimerStarted] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const serverUrl = "http://127.0.0.1:5000"; // Change this to your server address
    useEffect(() => {
        const fetchTimeLeft = async () => {
            try {
                const response = await axios.get(`${serverUrl}/time-left`);
                setTimeLeft(response.data["time-left"]); // Extract the value from the JSON object
                if (response.data["time-left"] > 0) {
                    // Extract the value from the JSON object
                    setTimerStarted(true);
                    const ipResponse = await axios.get(`${serverUrl}/ip`);
                    setIp(ipResponse.data);
                    setError("");
                }
            } catch (error) {
                console.error(
                    "The route is not reachable. This could be due to server downtime or incorrect server URL."
                );
                setError(
                    "The route is not reachable. This could be due to server downtime or incorrect server URL."
                );
            }
        };
        fetchTimeLeft();
    }, [serverUrl]);
    useEffect(() => {
        if (timerStarted) {
            const interval = setInterval(() => {
                setTimeLeft((timeLeft) => timeLeft - 1);
            }, 1000);
            const refreshInterval = setInterval(async () => {
                try {
                    const response = await axios.get(`${serverUrl}/time-left`);
                    setTimeLeft(response.data["time-left"]); // Extract the value from the JSON object
                    setError("");
                } catch (error) {
                    console.error(
                        "The route is not reachable. This could be due to server downtime or incorrect server URL."
                    );
                    setError(
                        "The route is not reachable. This could be due to server downtime or incorrect server URL."
                    );
                }
            }, 5000);
            return () => {
                clearInterval(interval);
                clearInterval(refreshInterval);
            };
        }
    }, [timerStarted, serverUrl]);
    const startServer = async () => {
        await axios.get(`${serverUrl}/start`);
        const response = await axios.get(`${serverUrl}/ip`);
        setIp(response.data);
        setTimeLeft(7200);
        setTimerStarted(true);
    };
    const stopServer = async () => {
        await axios.get(`${serverUrl}/stop`);
        setIp("");
        setTimeLeft(0);
        setTimerStarted(false);
    };
    const increaseTime = async () => {
        await axios.get(`${serverUrl}/increase-time`);
        setTimeLeft((timeLeft) => timeLeft + 3600);
    };
    return (
        <div>
            <button onClick={startServer}>Start Server</button>
            <button onClick={stopServer}>Stop Server</button>
            <button onClick={increaseTime}>Increase Time</button>
            <p>Server IP: {ip}</p>
            <p>Time left: {timeLeft} seconds</p>
            <p>{error}</p>
        </div>
    );
};
export default App;
