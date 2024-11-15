import { BrowserRouter, Route, Routes } from "react-router-dom";

import Customer from "./components/Map";
import Delivery from "./components/Route";
import Shop from "./components/Requests";


function App() {
    return (
      <div>
        <BrowserRouter>
        <div className="App">
          <Routes>
            <Route path="/" element={<Customer />} />
            <Route path="/route" element={<Delivery />} />
            <Route path="/requests" element={<Shop />} />
          </Routes>
        </div>
      </BrowserRouter>
      </div>
    );
}

export default App;
