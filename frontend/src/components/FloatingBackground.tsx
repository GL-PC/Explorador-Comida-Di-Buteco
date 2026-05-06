import chope from "../assets/chope-nobg.png";
import torresmo from "../assets/torresmo-nobg.png";
import caldo from "../assets/caldo-nobg.png";

export default function FloatingBackground() {
  return (
    <div className="floating-background" aria-hidden="true">
      <img src={chope} className="floating-item floating-chope" alt="" />
      <img src={torresmo} className="floating-item floating-torresmo" alt="" />
      <img src={caldo} className="floating-item floating-caldo" alt="" />

      <img src={chope} className="floating-item floating-chope-2" alt="" />
      <img src={torresmo} className="floating-item floating-torresmo-2" alt="" />
    </div>
  );
}