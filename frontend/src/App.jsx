import React, { useContext, useEffect, useState } from "react";

import Register from "./components/Register";
import Header from "./components/Header";
import { UserContext } from "./context/UserContext";
import Table from "./components/Table";

import Login from "./components/Login";

const App = () => {
  const [message, setMessage] = useState("");
  const [token] = useContext(UserContext);

  const getWelcomeMessage = async () => {
    const requestOptions = {
      method: "GET",
      // 'headers': {
      //   'Content-Type': 'application/json'
      // }
    };
    const response = await fetch("http://localhost:8000/api", requestOptions);
    // if I put '/api' instad of 'http://localhost:8000/api' it will not work, says some error related to < parsing the JSON
    const data = await response.json();

    // console.log(data);

    if (!response.ok) {
      console.log("something messed up");
    } else {
      setMessage(data.message);
    }
    // setMessage(responseData.message);
  };

  useEffect(() => {
    getWelcomeMessage();
  }, []);
  // getWelcomeMessage();

  return (
    <>
      <Header title={message} />
      <div className="columns">
        <div className="column"></div>
        <div className="column m-5 is-two-thirds">
          {!token ? (
            <div className="columns">
              <Register /> <Login />
            </div>
          ) : (
            <Table />
          )}
        </div>
        <div className="column"></div>
      </div>
    </>
  );
};


export default App;
