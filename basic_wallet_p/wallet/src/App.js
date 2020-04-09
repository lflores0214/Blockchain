import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";

function App() {
  const { register, handleSubmit } = useForm();
  const [user, setUser] = useState({ Username: "Luis" });
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  let base_url = "http://localhost:5000";
  useEffect(() => {
    axios
      .get("http://localhost:5000/chain")
      .then(res => {
        console.log(res.data.chain);
        let sum = 0;
        let trans = [];
        res.data.chain.forEach(element => {
          element.transactions.forEach(item => {
            if (item.recipient === user.Username) {
              sum += Number(item.amount);
              trans.push(item);
            }
          });
          setBalance(sum);
          setTransactions(trans);
        });
      })
      .catch(err => console.log(err));
  }, [user.Username]);

  const requestUserData = data => {
    axios
      .get(base_url + "/chain")
      .then(res => {
        console.log(res.data.chain);
        let sum = 0;
        let trans = [];
        res.data.chain.forEach(el => {
          el.transactions.forEach(item => {
            if (item.recipient === data.Username) {
              sum += Number(item.amount);
              trans.push(item);
            }
          });
          setBalance(sum);
          setTransactions(trans);
        });
      })
      .catch(err => {
        console.log("ERROR:", err);
      });
  };
  const onSubmit = data => {
    setBalance(0);
    setTransactions([]);
    setUser(data);
    requestUserData(data);
  };

  return (
    <div className="App">
      <h1>Coin Wallet</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <select name="Username" ref={register}>
          <option value="Luis">Luis</option>
          <option value="SomeDude">SomeDude</option>
          <option value="SomeOtherDude">SomeOtherDude</option>
        </select>
        <input type="submit" />
      </form>
      <p>
        {user.Username}'s balance: {balance}
      </p>
      <h4>All transactions for {user.Username}</h4>
      {transactions.map(item => {
        if (item.recipient === user.Username) {
          return (
            <div>
              <p>Amount: {item.amount}</p>
              <p>Recipient: {item.recipient}</p>
              <p>Sender: {item.sender}</p>
            </div>
          );
        }
      })}
    </div>
  );
}

export default App;
