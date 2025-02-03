import { select } from 'https://esm.sh/d3-selection';

let myData = [40, 10, 20, 60, 30];

select('.chart')
    .selectAll('circle')
    .data(myData)
    .join('circle')
    .attr('cx', function (d, i) {
        return i * 100;
    })
    .attr('cy', 50)
    .attr('r', function (d) {
        return 0.5 * d;
    })
    .style('fill', 'orange');
