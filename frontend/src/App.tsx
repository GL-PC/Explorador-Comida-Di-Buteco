import MapView from './components/MapView'
import FloatingBackground from "./components/FloatingBackground";

function App() {
  return (
    <main className="min-h-screen p-6">
      
      <header className='flex flex-col w-full gap-3 items-center justify-center mb-5'>
          <h1 className="text-5xl font-bold text-[#144a11] text-center">
              Explorador Comida di Buteco 2026
          </h1>
          <h2 className='text-lg font-normal text-black text-center'>
              Encontre os bares participantes do Comida di Buteco 2026!
          </h2>
      </header>

      <div className='w-full h-26 justify-center items-center flex mb-4'>
          <div className='w-[80%] h-full flex rounded-2xl bg-white'>

          </div>
      </div>

      <div className='w-full h-26 justify-center items-center flex mb-5'>
          <div className='w-[80%] h-full flex rounded-2xl bg-white'>

          </div>
      </div>
      <div className='w-[85%] h-[50vh] flex flex-row gap-4  mx-auto mb-4'>
          <div className=' w-[55%] p-4 flex flex-col bg-white rounded-[13px]'>
              <div className='flex justify-between align-middle pb-3'>
                  <div className='font-sans flex'>
                    <div className='flex gap-2 justify-center items-center px-3'>
                      <img src="/img-logo.png" alt="Comida di Buteco" className="h-4 w-auto"/>
                      <p>Mapa de Busca</p>
                    </div>
                      
                  </div>
                  <div className='font-sans flex gap-5'>
                    <div className='flex gap-2 justify-center items-center px-3'>
                        <img src="/img-logo.png" alt="Comida di Buteco" className="h-4 w-auto"/>
                        <p>Bares Participantes</p>
                    </div>
                    <div className='flex gap-2 justify-center items-center px-3'>
                        <img src="/img-logo.png" alt="Comida di Buteco" className="h-4 w-auto"/>
                        <p>Endereço Buscado</p>
                    </div>
                  </div>
              </div>
              <MapView />
          </div>
          <div className=' w-[45%] bg-white rounded-[13px]'>
              <div className=' w-full h-[90%]'>

              </div>
          </div>
      </div>

      <footer className="font-sans w-full flex items-center justify-center gap-4 py-4 text-sm text-[#000000]">
        <img
          src="/img-logo.png"
          alt="Comida di Buteco"
          className="h-6 w-auto"
        />
        <span >Comida Di Buteco 2026</span>
        <span>•</span>
        <span>
          Explore, descubra e apoie o melhor dos butecos!
        </span>
      </footer>
      <FloatingBackground />
    </main>
  )
}

export default App