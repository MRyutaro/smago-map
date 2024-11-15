import { slide as Menu } from "react-burger-menu";
import { Link } from "react-router-dom";

import GroupsIcon from "@mui/icons-material/Groups";
import BusinessIcon from "@mui/icons-material/Business";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";

const styles = {
    bmBurgerButton: {
        position: "fixed",
        width: "36px",
        height: "30px",
        left: "36px",
        top: "36px",
    },
    bmBurgerBars: {
        background: "#373a47",
    },
    bmBurgerBarsHover: {
        background: "#a90000",
    },
    bmCrossButton: {
        height: "24px",
        width: "24px",
    },
    bmCross: {
        background: "#bdc3c7",
    },
    bmMenu: {
        background: "#373a47",
        padding: "2.5em 1.5em 0",
        fontSize: "1.15em",
    },
    bmMorphShape: {
        fill: "#373a47",
    },
    bmItemList: {
        color: "#b8b7ad",
        padding: "0.8em",
    },
    bmItem: {
        display: "inline-block",
    },
    bmOverlay: {
        background: "rgba(0, 0, 0, 0.3)",
    },
};

const MenuComponent = () => {
    return (
        <Menu width={300} styles={styles}>
            {/* <div>
                <style>
                    {`
                    .menu-item {
                        color: #000;
                        transition: .3s;
                    }
                    .menu-item:hover {
                        background-position: -100% 0;
                        color: #ffb907;
                    }
                    .bm-item-list {
                        height: 50%;
                        padding: 10px 10px;
                        background-color: #fff;
                    }
                    .bm-menu {
                        overflow: hidden !important;
                    }
                    `}
                </style>
            </div> */}
            <Link to="/" className="menu-item">
                {/* 垂直方向に中央ぞろえ */}
                <div style={{ display: "flex", alignItems: "center", gap: "10px", margin: "30px 0", fontSize: "24px" }}>
                    <GroupsIcon /> For Tourist
                </div>
            </Link>
            <Link to="/requests" className="menu-item">
                <div style={{ display: "flex", alignItems: "center", gap: "10px", margin: "30px 0", fontSize: "24px" }}>
                    <BusinessIcon /> For Local Government
                </div>
            </Link>
            <Link to="/route" className="menu-item">
                <div style={{ display: "flex", alignItems: "center", gap: "10px", margin: "30px 0", fontSize: "24px" }}>
                    <LocalShippingIcon /> For Garbase Collector
                </div>
            </Link>
        </Menu>
    );
};

export default MenuComponent;
