#include "FlavorNode.h"
#include <QDebug>

FlavorNode::FlavorNode(QObject *parent)
    : QObject(parent)
{
    int argc = 0;
    rclcpp::init(argc, nullptr);

    m_node = rclcpp::Node::make_shared("icecream_dashboard_node");

    m_publisher = m_node->create_publisher<std_msgs::msg::String>(
        "/icecream/selected_flavor", 10
    );

    m_stateSub = m_node->create_subscription<std_msgs::msg::String>(
        "/icecream/robot_state", 10,
        [this](const std_msgs::msg::String::SharedPtr msg) {
            QString newState = QString::fromStdString(msg->data);
            if (newState != m_robotState) {
                m_robotState = newState;
                qDebug() << "[ROS2] Robot state:" << m_robotState;
                QMetaObject::invokeMethod(this, [this]() {
                    emit robotStateChanged(m_robotState);
                }, Qt::QueuedConnection);
            }
        }
    );

    m_spinThread = std::thread([this]() {
        rclcpp::spin(m_node);
    });

    qDebug() << "[ROS2] icecream_dashboard_node started";
    qDebug() << "[ROS2] Publishing to:  /icecream/selected_flavor";
    qDebug() << "[ROS2] Subscribing to: /icecream/robot_state";
}

FlavorNode::~FlavorNode()
{
    rclcpp::shutdown();
    if (m_spinThread.joinable())
        m_spinThread.join();
}

void FlavorNode::selectFlavor(const QString &flavor)
{
    m_selectedFlavor = flavor;
    auto msg = std_msgs::msg::String();
    msg.data = flavor.toStdString();
    m_publisher->publish(msg);
    qDebug() << "[ROS2] Published flavor:" << flavor;
    emit flavorChanged(flavor);
}
