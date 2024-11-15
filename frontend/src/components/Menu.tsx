import { slide as Menu } from "react-burger-menu";
import { Link } from "react-router-dom";

import GroupsIcon from "@mui/icons-material/Groups";
import BusinessIcon from "@mui/icons-material/Business";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";

const MenuComponent = () => {
    return (
        <Menu width={300}>
            <div>
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
            </div>
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
