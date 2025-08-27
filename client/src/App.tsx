import {TransfersTable} from "./components/dashboard/TransfersTable"
import { Navbar } from "./components/layout/Navbar"
function App() {

  return (
    <>
      <div>
        <Navbar />
        <main className="container mx-auto p-4 border">
          <TransfersTable />
        </main>
      </div>
    </>
  )
}

export default App
