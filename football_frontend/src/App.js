import React, { useState } from 'react';
import axios from 'axios';
import  './index.css';
function App() {
    const [league, setLeague] = useState("Premier League");
    const [file2, setFile2] = useState(null); // Current standings
    const [file3, setFile3] = useState(null); // Remaining fixtures
    const [responseData, setResponseData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false); // State for expanding simulation results

    const handleFileChange = (e, setFile) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file2 || !file3) {
            alert("Please select both current standings and remaining fixtures files.");
            return;
        }
        const formData = new FormData();
        formData.append("league", league);
        formData.append("file2", file2);
        formData.append("file3", file3);
        setLoading(true);
        try {
            const res = await axios.post("http://localhost:8080/api/upload", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setResponseData(res.data);
        } catch (error) {
            console.error("Error uploading files", error);
            alert("An error occurred during file upload.");
        }
        setLoading(false);
    };

    return (
        <div className="p-6 max-w-6xl mx-auto">
            {/* Header */}
            <h1 className="text-3xl font-bold text-center mb-8">Win Wise - League Standings Predictor</h1>

            {/* Form Section */}
            <form onSubmit={handleSubmit} className="bg-gray-100 p-6 rounded-lg shadow-md mb-8">
                {/* League Selector */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Select League:</label>
                    <select
                        value={league}
                        onChange={(e) => setLeague(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    >
                        <option value="Premier League">Premier League</option>
                        <option value="La Liga">La Liga</option>
                        <option value="Bundesliga">Bundesliga</option>
                    </select>
                </div>

                {/* File Uploads */}
                <div className="space-y-4">
                    {/* Current Standings File */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Upload Current Standings (CSV/XLSX):
                        </label>
                        <input
                            type="file"
                            onChange={(e) => handleFileChange(e, setFile2)}
                            accept=".csv,.xlsx"
                            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-green-500"
                        />
                    </div>

                    {/* Remaining Fixtures File */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Upload Remaining Fixtures (CSV/XLSX):
                        </label>
                        <input
                            type="file"
                            onChange={(e) => handleFileChange(e, setFile3)}
                            accept=".csv,.xlsx"
                            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-red-500"
                        />
                    </div>
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600 focus:outline-none ${
                        loading && "cursor-not-allowed opacity-50"
                    }`}
                >
                    {loading ? "Processing..." : "Submit"}
                </button>
            </form>

            {/* Results Section */}
            {responseData && (
                <div className="space-y-6">
                    {/* Success Message */}
                    <div>
                        <p className="text-green-500 text-center font-medium mb-4">
                            {responseData.message}
                        </p>
                    </div>

                    {/* Simulation Results (Collapsible) */}
                    <div className="bg-blue-100 p-6 rounded-lg shadow-md">
                        <h2 className="text-2xl font-semibold mb-4">Simulation Results</h2>
                        {responseData.simulatedResults &&
                        responseData.simulatedResults.length > 0 ? (
                            <div>
                                {/* Display truncated results */}
                                <ul className="list-disc pl-6 space-y-2">
                                    {responseData.simulatedResults
                                        .slice(0, isExpanded ? undefined : 5) // Show all if expanded, else show first 5
                                        .map((result, index) => (
                                            <li key={index} className="text-blue-700">
                                                {result.HomeTeam} {result.HomeGoals} - {result.AwayGoals}{" "}
                                                {result.AwayTeam}
                                            </li>
                                        ))}
                                </ul>
                                {/* Expand/Collapse Button */}
                                {responseData.simulatedResults.length > 5 && (
                                    <button
                                        onClick={() => setIsExpanded(!isExpanded)}
                                        className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 focus:outline-none"
                                    >
                                        {isExpanded ? "Collapse" : "Show More Results"}
                                    </button>
                                )}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-center">No match simulation results available.</p>
                        )}
                    </div>

                    {/* Predicted League Standings Table */}
                    <div className="bg-green-100 p-6 rounded-lg shadow-md">
                        <h2 className="text-2xl font-semibold mb-4">Predicted League Standings</h2>
                        {responseData.predictedStandings &&
                        responseData.predictedStandings.length > 0 ? (
                            <table className="min-w-full border border-gray-300 bg-white shadow-md rounded-lg overflow-x-auto">
                                <thead className="bg-green-200">
                                <tr>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        Rank
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        Team
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        P
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        W
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        D
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        L
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        F
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        A
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        GD
                                    </th>
                                    <th className="border-b border-gray-300 px-4 py-2 text-left font-semibold text-gray-700">
                                        Points
                                    </th>
                                </tr>
                                </thead>
                                <tbody>
                                {responseData.predictedStandings.map((team, index) => (
                                    <tr
                                        key={index}
                                        className="hover:bg-gray-100 transition duration-300"
                                    >
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.Rank}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.Team}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.P}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.W}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.D}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.L}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.F}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.A}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.GD}
                                        </td>
                                        <td className="border-b border-gray-200 px-4 py-2 text-gray-700">
                                            {team.Points}
                                        </td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        ) : (
                            <p className="text-gray-500 text-center">No standings available.</p>
                        )}
                    </div>

                    {/* Predicted Points Plot */}
                    <div className="bg-yellow-100 p-6 rounded-lg shadow-md">
                        <h3 className="text-2xl font-semibold mb-4">Predicted Points Plot</h3>
                        {responseData.plot && (
                            <img
                                src={responseData.plot}
                                alt="Predicted Points Plot"
                                className="max-w-full rounded-lg shadow-lg"
                            />
                        )}
                        {!responseData.plot && (
                            <p className="text-gray-500 text-center">No plot available.</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;