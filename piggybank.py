import argparse
from solid2 import *
import pyqrcode
from os import path

wall_width = 4
radius = 8
dia = 2 * radius

def generate_label(content):
    pass


def generate_qr_code(content):
    lines = pyqrcode.create(content).text().split()
    bits=[]
    bit=cube([1.1,1.1,1.1])
    for y in range(len(lines)):
        for x in range(len(lines[y])):
            if lines[y][x] == "1":
                bits.append(bit.translate([x,-y,0]))

    obj = union()(
            *bits
    )

    return len(lines), color("black") (
        obj
    )


def generate_label(content):
    return color("black") (text(text=content,halign='center',valign='bottom'))


def generate_piggybank(width, length, height, qr_content=None, label_content=None):
    block = difference()(
        linear_extrude(height) (translate([radius, radius]) (minkowski() (
            square([width - dia, length - dia]),
            circle(r=radius)
        ))),
        translate([radius + wall_width, radius + wall_width, wall_width]) (linear_extrude(height) (minkowski() (
            square([width - dia - (wall_width * 2), length - dia - (wall_width * 2)]),
            circle(r=radius)
        ))),
    )

    block = difference()(
        block,
        translate([(width - 30) / 2, (height / 2) * 2, 0])(
            cube([30,5,5])
      )
    )

    qr_code = None
    if qr_content:
        size, qr_code = generate_qr_code(qr_content)
        qr_code = translate([(width - size) / 2, size + 5, 0]) (
            qr_code
        )
        block = union()(
            block,
            qr_code
        )

    label = None
    if label_content:
        label = generate_label(label_content)
        label = translate([width  / 2, length - 15, 0]) (label)
        block = union()(
            block,
            label
        )

    block=mirror([1,0,0]) (block)

    block=difference() (
        block,
        debug() (translate([-1 * width, 0, height - 5]) (generate_lid(width, length)))
    )

    inlay = None
    if label or qr_code:
        inlay = mirror([1,0,0]) (label + qr_code)

    return block, inlay


def generate_lid(width, length):
    height = 5
    block = linear_extrude(height) (translate([radius, radius]) (minkowski() (
        square([width - dia, length - dia]),
        circle(r=radius)
    )))

    rail = union() (
        cube([wall_width / 2, length, height / 2]),
        translate([0, 0, height / 2]) (cube([wall_width, length, height / 2]))
    )

    block = difference() (
        block,
        rail,
        translate([width,0,0]) (mirror([1,0,0]) (rail)),
        translate([0, length - wall_width, 0]) (cube([width, wall_width, height])),
        translate([width / 2, length / 2, height/2]) (cylinder(r=10, h=height/2))
    )

    return block


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='piggybank generator',
        description='generates a piggybank with labels'
    )

    parser.add_argument('output_name')
    parser.add_argument('-qr', '--qr')
    parser.add_argument('-l', '--label')
    parser.add_argument('-W', '--width', default=80)
    parser.add_argument('-L', '--length', default=80)
    parser.add_argument('-H', '--height', default=80)

    args = parser.parse_args()

    case, inlay = generate_piggybank(args.width, args.length, int(args.height), args.qr, args.label)
    generate_lid(args.width, args.length).save_as_stl(filename=path.join('out', f'{args.output_name}-lid.stl'))

    case.save_as_stl(filename=path.join('out', f'{args.output_name}-case.stl'))

    if inlay:
        inlay.save_as_stl(filename=path.join('out', f'{args.output_name}-inlay.stl'))
