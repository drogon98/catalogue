import React from "react";
import BeautyStars from "beauty-stars";

import "./Rating.css";

class Rating extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: this.props.value,
    };
    this.ratingChanged = this.ratingChanged.bind(this);
  }

  ratingChanged(val) {
    if (!this.props.clickable) {
      return;
    }
    this.setState({
      value: val,
    });
    console.log(this.state.value);
  }

  render() {
    return (
      <div style={{ display: "flex", alignItems: "center" }}>
        <BeautyStars
          value={this.state.value}
          onChange={(val) => this.ratingChanged(val)}
          size={this.props.size}
          activeColor={"#d31c27"}
          inactiveColor={"#d4d4d4"}
          editable={this.props.editable}
          gap={this.props.gap}
        />
      </div>
    );
  }
}

export default Rating;
