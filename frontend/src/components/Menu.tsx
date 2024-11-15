import { slide as Menu } from "react-burger-menu";
import { Link } from "react-router-dom";

import GroupsIcon from "@mui/icons-material/Groups";
import BusinessIcon from "@mui/icons-material/Business";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";

const styles = {
    bmBurgerButton: {
        position: "fixed",
        margin: "8px",
        width: "36px",
        height: "30px",
        left: "20px",
        top: "20px",
    },
    bmBurgerBars: {
        background: "#3a5bf0",
    },
    bmBurgerBarsHover: {
        background: "#a90000",
    },
    bmMenu: {
        background: "#fff",
        overflow: "hidden",
    },
    bmItemList: {
        padding: "10px",
    },
    bmItem: {
        color: "#5c5c5c",
        fontSize: "24px",
        marginBottom: "30px",
    },
    bmOverlay: {
        background: "rgba(0, 0, 0, 0.4)",
        overflow: "hidden",
    },
};

const MenuComponent = () => {
    return (
        <Menu width={300} styles={styles}>
            <div>
                <style>
                    {`
                    .menu-item {
                        color: #000 !important;
                        transition: .3s all;
                    }
                    .menu-item:hover {
                        background-position: -100% 0 !important;
                        color: #ffb907 !important;
                    }
                    `}
                </style>
            </div>
            <Link to="/" className="menu-item">
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        margin: "30px 0",
                    }}
                >
                    <GroupsIcon /> For Tourist
                </div>
            </Link>
            <Link to="/requests" className="menu-item">
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                    }}
                >
                    <BusinessIcon /> For Local Government
                </div>
            </Link>
            <Link to="/route" className="menu-item">
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                    }}
                >
                    <LocalShippingIcon /> For Garbase Collector
                </div>
            </Link>
        </Menu>
    );
};

export default MenuComponent;
