import React from 'react';

import Requirement from './requirement';
import Pagers from '../pagers';
import ThingCounter from '../thing-counters';

export default function RequirementsView({ requirements, count }) {
  const singular = 'requirement';
  const plural = 'requirements';
  return (
    <div>
      <ThingCounter count={count} singular={singular} plural={plural} />
      <ul className="requirement-list list-reset">
        { requirements.map(requirement =>
          <li key={requirement.req_id} className="gray-border border rounded mb2">
            <Requirement requirement={requirement} />
          </li>) }
      </ul>
      <Pagers count={count} />
    </div>
  );
}
RequirementsView.propTypes = {
  requirements: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number,
    title: React.PropTypes.string,
    relevant_reqs: React.PropTypes.number,
  })),
  count: React.PropTypes.number,
};
RequirementsView.defaultProps = {
  requirements: [],
  count: 0,
};
