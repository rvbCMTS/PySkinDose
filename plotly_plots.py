import plotly.graph_objs as go
import plotly.offline as ply
from phantom_class import Phantom
from beam_class import Beam
import numpy as np
import pandas as pd


def plot_geometry(patient: Phantom, table: Phantom, pad: Phantom,
                  data_norm: pd.DataFrame, mode: str, event: int = 0,
                  include_patient: bool = False) -> None:
    """Visualize the geometry from the irradiation events.

    This function plots the phantom, table, pad, beam and detector. The type of
    plot is specified in the parameter mode.

    Parameters
    ----------
    patient : Phantom
        Patient phantom from instance of class Phantom. Can be of
        phantom_type "plane", "cylinder" or "human"
    table : Phantom
        Table phantom from instance of class Phantom. phantom_type must be
        "table"
    pad : Phantom
        Pad phantom from instance of class Phantom. phantom_type must be
        "pad"
    data_norm : pd.DataFrame
        Table containing dicom RDSR information from each irradiation event
        See parse_data.py for more information.
    mode : str
        Choose between "plot_setup", "plot_event" and "plot_procedure".

         "plot_setup" plots the patient, table and pad in reference position
         together with the X-ray system with zero angulation. This is a
         debugging feature

        "plot_event" plots a specific irradiation event, in which the patient,
        table, pad, and beam are positioned according to the irradiation event
        specified by the parameter event

        "plot_procedure" plots out the X-ray system, table and pad for all
        irradiation events in the procedure The visible event are chosen by a
        event slider

    event : int, optional
        choose specific irradiation event if mode "plot_event" are used
        Default is 0, in which the first irradiation event is considered.

    include_patient : bool, optional
        Choose if the patient phantom should be included in the plot_procedure
        function. WARNING, very heavy on memory. Default is False.

    """
    # Define colors
    source_color = '#D3D3D3'
    table_color = '#D3D3D3'
    detector_color = '#D3D3D3'
    pad_color = 'slateblue'
    beam_color = 'red'
    patient_color = "#CE967C"

    # Camera view settings
    camera = dict(up=dict(x=0, y=-1, z=0),
                  center=dict(x=0, y=0, z=0),
                  eye=dict(x=-1.3, y=-1.3, z=0.7))

    beam = Beam(data_norm, event=0, plot_setup=True)

    # Define hoover texts for patient, table and pad
    patient_text = [f"<b>Patient phantom</b><br><br><b>LAT:</b> {np.around(patient.r[ind, 2])} cm<br><b>LON:</b> {np.around(patient.r[ind, 0])} cm<br><b>VER:</b> {np.around(patient.r[ind, 1])} cm" for ind in range(len(patient.r))]
    table_text = [f"<b>Support table</b><br><br><b>LAT:</b> {np.around(table.r[ind, 2])} cm <br><b>LON:</b> {np.around(table.r[ind, 0])} cm <br><b>VER:</b> {np.around(table.r[ind, 1])} cm" for ind in range(len(table.r))]       
    pad_text = [f"<b>Support pad</b><br><br><b>LAT:</b> {np.around(pad.r[ind, 2])} cm <br><b>LON:</b> {np.around(pad.r[ind, 0])} cm <br><b>VER:</b> {np.around(pad.r[ind, 1])} cm" for ind in range(len(pad.r))]

    if mode in ['plot_setup', 'plot_event']:

        if mode == 'plot_setup':
            print("plotting geometry setup...")

            # Create beam
            beam = Beam(data_norm, event=0, plot_setup=True)

            # Define hoover texts and plot title
            source_text = [f"<b>X-ray source</b><br><br><b>LAT:</b> {np.around(beam.r[0, 2])} cm <br><b>LON:</b> {np.around(beam.r[0, 0])} cm <br><b>VER:</b> {np.around(beam.r[0, 1])} cm"]
            beam_text = [f"<b>X-ray beam vertex</b><br><br><b>LAT:</b> {np.around(beam.r[ind, 2])} cm <br><b>LON:</b> {np.around(beam.r[ind, 0])} cm <br><b>VER:</b> {np.around(beam.r[ind, 1])} cm" for ind in range(len(beam.r))]
            detectors_text = [f"<b>X-ray detector</b><br><br><b>LAT:</b> {np.around(beam.det_r[ind, 2])} cm <br><b>LON:</b> {np.around(beam.det_r[ind, 0])} cm <br><b>VER:</b> {np.around(beam.det_r[ind, 1])} cm" for ind in range(len(beam.det_r))]
            title = f"""<b>P</b>y<b>S</b>kin<b>D</b>ose[dev]<br>mode: {mode}"""

        elif mode == 'plot_event':
            print(f"plotting event {event+1} of {len(data_norm)}...")

            # Create beam
            beam = Beam(data_norm, event=event, plot_setup=False)

            # Define hoover texts and plot title
            source_text = [f"<b>X-ray source</b><br><br><b>LAT:</b> {np.around(beam.r[0, 2])} cm <br><b>LON:</b> {np.around(beam.r[0, 0])} cm <br><b>VER:</b> {np.around(beam.r[0, 1])} cm"]
            beam_text = [f"<b>X-ray beam vertex</b><br><br><b>LAT:</b> {np.around(beam.r[ind, 2])} cm <br><b>LON:</b> {np.around(beam.r[ind, 0])} cm <br><b>VER:</b> {np.around(beam.r[ind, 1])} cm" for ind in range(len(beam.r))]
            detectors_text = [f"<b>X-ray detector</b><br><br><b>LAT:</b> {np.around(beam.det_r[ind, 2])} cm <br><b>LON:</b> {np.around(beam.det_r[ind, 0])} cm <br><b>VER:</b> {np.around(beam.det_r[ind, 1])} cm" for ind in range(len(beam.det_r))]
            title = f'<b>P</b>y<b>S</b>kin<b>D</b>ose[dev]<br>mode: {mode}, event {event+1} of {len(data_norm)}'

            # Position geometry
            patient.position_phantom(data_norm, event)
            table.position_phantom(data_norm, event)
            pad.position_phantom(data_norm, event)

        # Create patient mesh
        patient_mesh = go.Mesh3d(
            x=patient.r[:, 0], y=patient.r[:, 1], z=patient.r[:, 2],
            i=patient.ijk[:, 0], j=patient.ijk[:, 1], k=patient.ijk[:, 2],
            color=patient_color, hoverinfo="text",
            text=patient_text,
            lighting=dict(diffuse=0.5, ambient=0.5))

        # Create X-ray source mesh
        source_mesh = go.Scatter3d(
            x=[beam.r[0, 0], beam.r[0, 0]],
            y=[beam.r[0, 1], beam.r[0, 1]],
            z=[beam.r[0, 2], beam.r[0, 2]],
            hoverinfo="text",
            mode="markers",
            marker=dict(size=8, color=source_color),
            text=source_text)

        # Create support table mesh
        table_mesh = go.Mesh3d(
            x=table.r[:, 0], y=table.r[:, 1], z=table.r[:, 2],
            i=table.ijk[:, 0], j=table.ijk[:, 1], k=table.ijk[:, 2],
            color=table_color, hoverinfo="text",
            text=table_text)

        # Create X-ray detector mesh
        detector_mesh = go.Mesh3d(
            x=beam.det_r[:, 0], y=beam.det_r[:, 1], z=beam.det_r[:, 2],
            i=beam.det_ijk[:, 0], j=beam.det_ijk[:, 1], k=beam.det_ijk[:, 2],
            color=detector_color, hoverinfo="text",
            text=detectors_text)

        # Create support pad mesh
        pad_mesh = go.Mesh3d(
            x=pad.r[:, 0], y=pad.r[:, 1], z=pad.r[:, 2],
            i=pad.ijk[:, 0], j=pad.ijk[:, 1], k=pad.ijk[:, 2],
            name="Support pad",
            color=pad_color, hoverinfo="text",
            text=pad_text)

        # Create X-ray beam mesh
        beam_mesh = go.Mesh3d(
            x=beam.r[:, 0], y=beam.r[:, 1], z=beam.r[:, 2],
            i=beam.ijk[:, 0], j=beam.ijk[:, 1], k=beam.ijk[:, 2],
            color=beam_color, hoverinfo="text", opacity=0.3,
            text=beam_text)

        # Add wireframes to mesh objects
        wf_beam, wf_table, wf_pad, wf_detector = create_wireframes(
            beam, table, pad, line_width=4, visible=True)

        # Layout settings
        layout = go.Layout(
            font=dict(family='roboto', size=14),
            showlegend=False,
            hoverlabel=dict(font=dict(size=16)),
            dragmode="orbit",
            title=title,
            titlefont=dict(family='Courier New, monospace', size=35,
                           color='white'),
            plot_bgcolor='rgb(45,45,45)',
            paper_bgcolor='rgb(45,45,45)',

            scene=dict(aspectmode="data", camera=camera,

                       xaxis=dict(title='X - LON [cm]',
                                  color="white",
                                  zerolinecolor="limegreen", zerolinewidth=3),

                       yaxis=dict(title="Y - VER [cm]",
                                  color="white",
                                  zerolinecolor="limegreen", zerolinewidth=3),

                       zaxis=dict(title='Z - LAT [cm]',
                                  color="white",
                                  zerolinecolor="limegreen", zerolinewidth=3)))

        data = [patient_mesh, source_mesh, table_mesh, detector_mesh, pad_mesh,
                beam_mesh, wf_beam, wf_table, wf_pad, wf_detector]

        fig = go.Figure(data=data, layout=layout)
        # execute plot
        ply.plot(fig, filename=f'{mode}.html')

    if mode == "plot_procedure":
        print(f'plotting entire procedure with {len(data_norm)}'
              ' irradiation events...')

        # Define hoover texts and title
        source_text = [f"<b>X-ray source</b><br><br><b>LAT:</b> {np.around(beam.r[0, 2])} cm <br><b>LON:</b> {np.around(beam.r[0, 0])} cm <br><b>VER:</b> {np.around(beam.r[0, 1])} cm"]
        beam_text = [f"<b>X-ray beam vertex</b><br><br><b>LAT:</b> {np.around(beam.r[ind, 2])} cm <br><b>LON:</b> {np.around(beam.r[ind, 0])} cm <br><b>VER:</b> {np.around(beam.r[ind, 1])} cm" for ind in range(len(beam.r))]
        detectors_text = [f"<b>X-ray detector</b><br><br><b>LAT:</b> {np.around(beam.det_r[ind, 2])} cm <br><b>LON:</b> {np.around(beam.det_r[ind, 0])} cm <br><b>VER:</b> {np.around(beam.det_r[ind, 1])} cm" for ind in range(len(beam.det_r))]
        title = f"""<b>P</b>y<b>S</b>kin<b>D</b>ose[dev]<br>mode: {mode}"""

        source_mesh = [0] * len(data_norm)
        table_mesh = [0] * len(data_norm)
        patient_mesh = [0] * len(data_norm)
        detector_mesh = [0] * len(data_norm)
        pad_mesh = [0] * len(data_norm)
        beam_mesh = [0] * len(data_norm)
        wf_beam = [0] * len(data_norm)
        wf_table = [0] * len(data_norm)
        wf_pad = [0] * len(data_norm)
        wf_detector = [0] * len(data_norm)

        # For each irradiation event
        for i in range(len(data_norm)):

            # Position geometry objects
            beam = Beam(data_norm, event=i, plot_setup=False)
            table.position_phantom(data_norm, i)
            pad.position_phantom(data_norm, i)

            if include_patient:
                patient.position_phantom(data_norm, i)

                # Create patient mesh
                patient_mesh[i] = go.Mesh3d(
                    x=patient.r[:, 0], y=patient.r[:, 1], z=patient.r[:, 2],
                    i=patient.ijk[:, 0], j=patient.ijk[:, 1],
                    k=patient.ijk[:, 2], color=patient_color, hoverinfo="text",
                    visible=False, text=patient_text,
                    lighting=dict(diffuse=0.5, ambient=0.5))

            # Create X-ray source mesh
            source_mesh[i] = go.Scatter3d(
                x=[beam.r[0, 0], beam.r[0, 0]],
                y=[beam.r[0, 1], beam.r[0, 1]],
                z=[beam.r[0, 2], beam.r[0, 2]],
                mode="markers", hoverinfo="text", visible=False,
                marker=dict(size=8, color=source_color),
                text=source_text)

            # Create support table mesh
            table_mesh[i] = go.Mesh3d(
                x=table.r[:, 0], y=table.r[:, 1], z=table.r[:, 2],
                i=table.ijk[:, 0], j=table.ijk[:, 1], k=table.ijk[:, 2],
                color=table_color, hoverinfo="text", visible=False,
                text=table_text)

            # Create X-ray detector mesh
            detector_mesh[i] = go.Mesh3d(
                x=beam.det_r[:, 0], y=beam.det_r[:, 1], z=beam.det_r[:, 2],
                i=beam.det_ijk[:, 0],
                j=beam.det_ijk[:, 1],
                k=beam.det_ijk[:, 2],
                color=detector_color, hoverinfo="text", visible=False,
                text=detectors_text)

            # Create support pad mesh
            pad_mesh[i] = go.Mesh3d(
                x=pad.r[:, 0], y=pad.r[:, 1], z=pad.r[:, 2],
                i=pad.ijk[:, 0], j=pad.ijk[:, 1], k=pad.ijk[:, 2],
                color=pad_color, hoverinfo="text", visible=False,
                text=pad_text)

            # Create X-ray beam mesh
            beam_mesh[i] = go.Mesh3d(
                x=beam.r[:, 0], y=beam.r[:, 1], z=beam.r[:, 2],
                i=beam.ijk[:, 0], j=beam.ijk[:, 1], k=beam.ijk[:, 2],
                color=beam_color, hoverinfo="text", visible=False, opacity=0.3,
                text=beam_text)

            # Add wireframes to mesh objects
            wf_beam[i], wf_table[i], wf_pad[i], wf_detector[i] = \
                create_wireframes(beam, table, pad, 
                                  line_width=4, visible=False)

        # Set first irradiation event initally visible
        source_mesh[0].visible = table_mesh[0].visible = pad_mesh[0].visible \
            = detector_mesh[0].visible = beam_mesh[0].visible = \
            wf_beam[0].visible = wf_table[0].visible = wf_pad[0].visible = \
            wf_detector[0].visible = True

        if include_patient:
            patient_mesh[0].visible = True

        steps = []

        # Event slider settings
        for i in range(len(data_norm)):
            step = dict(method='restyle',
                        args=['visible', [False] * len(data_norm)],
                        label=i + 1)
            step['args'][1][i] = True  # Toggle i'th trace to "visible"
            steps.append(step)

        sliders = [dict(active=0,
                        transition=dict(duration=300, easing="quad-in-out"),
                        bordercolor="rgb(45,45,45)",
                        borderwidth=3,
                        tickcolor="white",
                        bgcolor="red",
                        currentvalue=dict(prefix="Active event: ",
                                          suffix=f" of  {len(data_norm)}",
                                          font=dict(color="white", size=30)),
                        font=dict(color="white", size=16),
                        pad=dict(b=10, t=10, l=250, r=250),
                        steps=steps)]

        # Layout settings
        layout = go.Layout(
            sliders=sliders,
            font=dict(family='roboto', size=14),
            hoverlabel=dict(font=dict(size=16)),
            showlegend=False,
            dragmode="orbit",
            title=title,
            titlefont=dict(family='Courier New, monospace', size=35,
                           color='white'),
            plot_bgcolor='rgb(45,45,45)',
            paper_bgcolor='rgb(45,45,45)',

            scene=dict(aspectmode="cube", camera=camera,

                       xaxis=dict(title='X - LON [cm]',
                                  range=[-150, 150],
                                  color="white",
                                  zerolinecolor="limegreen", zerolinewidth=3),

                       yaxis=dict(title="Y - VER [cm]",
                                  range=[-150, 150],
                                  color="white",
                                  zerolinecolor="limegreen", zerolinewidth=3),

                       zaxis=dict(title='Z - LAT [cm]',
                                  range=[-150, 150],
                                  color="white",
                                  zerolinecolor="limegreen", zerolinewidth=3)))
        if include_patient:
            data = source_mesh + table_mesh + pad_mesh + patient_mesh + \
                beam_mesh + detector_mesh + wf_table + wf_pad + wf_beam + \
                wf_detector

        else:
            data = source_mesh + table_mesh + pad_mesh + beam_mesh + \
                detector_mesh + wf_table + wf_pad + wf_beam + wf_detector

        fig = go.Figure(data=data, layout=layout)
        # Execute plot
        ply.plot(fig, filename=f'{mode}.html')


def create_wireframes(beam: Beam, table: Phantom, pad: Phantom,
                      line_width: int = 4, visible: bool = True):
    """Create wireframe versions of the mesh3d objects in plot_geometry.

    The purpose of this function is to enhance the plot_geometry plot by
    adding wireframes.

    Parameters
    ----------
    beam: Beam
        X-ray beam, i.e. instance of class Beam. See beam_class for more info
    table: Phantom
        Table phantom from instance of class Phantom. phantom_type must be
        "table"
    pad: Phantom
        Table phantom from instance of class Phantom. phantom_type must be
        "pad"
    line_width : int, optional
        Line width of the wireframes. Default value is 4.
    visible : bool, optional
        Set the visibility of each of the wireframe traces

    """
    # Color settings
    wf_beam_color = 'red'
    wf_table_color = '#3f3f3f'
    wf_pad_color = '#3f3f3f'
    wf_detector_color = 'darkslategray'

    # The following section creates a wireframe plot for the X-ray beam
    temp_x = [beam.r[0, 0], beam.r[1, 0], beam.r[0, 0], beam.r[2, 0],
              beam.r[0, 0], beam.r[3, 0], beam.r[0, 0], beam.r[4, 0],
              beam.r[1, 0], beam.r[2, 0], beam.r[3, 0], beam.r[4, 0],
              beam.r[1, 0]]

    temp_y = [beam.r[0, 1], beam.r[1, 1], beam.r[0, 1], beam.r[2, 1],
              beam.r[0, 1], beam.r[3, 1], beam.r[0, 1], beam.r[4, 1],
              beam.r[1, 1], beam.r[2, 1], beam.r[3, 1], beam.r[4, 1],
              beam.r[1, 1]]

    temp_z = [beam.r[0, 2], beam.r[1, 2], beam.r[0, 2], beam.r[2, 2],
              beam.r[0, 2], beam.r[3, 2], beam.r[0, 2], beam.r[4, 2],
              beam.r[1, 2], beam.r[2, 2], beam.r[3, 2], beam.r[4, 2],
              beam.r[1, 2]]

    wf_beam = go.Scatter3d(x=temp_x, y=temp_y, z=temp_z, mode="lines",
                           hoverinfo="skip", visible=visible,
                           line=dict(color=wf_beam_color, width=line_width))

    # The following section creates a wireframe plot for the support table
    x1 = table.r[0:8, 0].tolist() + [table.r[0, 0]]
    y1 = table.r[0:8, 1].tolist() + [table.r[0, 1]]
    z1 = table.r[0:8, 2].tolist() + [table.r[0, 2]]

    x2 = table.r[8:16, 0].tolist() + [table.r[8, 0]]
    y2 = table.r[8:16, 1].tolist() + [table.r[8, 1]]
    z2 = table.r[8:16, 2].tolist() + [table.r[8, 2]]

    x3 = [table.r[8, 0], table.r[9, 0], table.r[10, 0], table.r[2, 0], table.r[3, 0], table.r[11, 0], table.r[12, 0], table.r[13, 0], table.r[5, 0], table.r[6, 0], table.r[14, 0], table.r[15, 0], table.r[7, 0]]
    y3 = [table.r[8, 1], table.r[9, 1], table.r[10, 1], table.r[2, 1], table.r[3, 1], table.r[11, 1], table.r[12, 1], table.r[13, 1], table.r[5, 1], table.r[6, 1], table.r[14, 1], table.r[15, 1], table.r[7, 1]]
    z3 = [table.r[8, 2], table.r[9, 2], table.r[10, 2], table.r[2, 2], table.r[3, 2], table.r[11, 2], table.r[12, 2], table.r[13, 2], table.r[5, 2], table.r[6, 2], table.r[14, 2], table.r[15, 2], table.r[7, 2]]

    temp_x = x1 + x2 + x3
    temp_y = y1 + y2 + y3
    temp_z = z1 + z2 + z3

    wf_table = go.Scatter3d(x=temp_x, y=temp_y, z=temp_z, mode="lines",
                            hoverinfo="skip", visible=visible,
                            line=dict(color=wf_table_color, width=line_width))

    # The following section creates a wireframe plot for the support pad
    x1 = pad.r[0:8, 0].tolist() + [pad.r[0, 0]]
    y1 = pad.r[0:8, 1].tolist() + [pad.r[0, 1]]
    z1 = pad.r[0:8, 2].tolist() + [pad.r[0, 2]]

    x2 = pad.r[8:16, 0].tolist() + [pad.r[8, 0]]
    y2 = pad.r[8:16, 1].tolist() + [pad.r[8, 1]]
    z2 = pad.r[8:16, 2].tolist() + [pad.r[8, 2]]

    x3 = [pad.r[8, 0], pad.r[9, 0], pad.r[10, 0], pad.r[2, 0], pad.r[3, 0], pad.r[11, 0], pad.r[12, 0], pad.r[13, 0], pad.r[5, 0], pad.r[6, 0], pad.r[14, 0], pad.r[15, 0], pad.r[7, 0]]
    y3 = [pad.r[8, 1], pad.r[9, 1], pad.r[10, 1], pad.r[2, 1], pad.r[3, 1], pad.r[11, 1], pad.r[12, 1], pad.r[13, 1], pad.r[5, 1], pad.r[6, 1], pad.r[14, 1], pad.r[15, 1], pad.r[7, 1]]
    z3 = [pad.r[8, 2], pad.r[9, 2], pad.r[10, 2], pad.r[2, 2], pad.r[3, 2], pad.r[11, 2], pad.r[12, 2], pad.r[13, 2], pad.r[5, 2], pad.r[6, 2], pad.r[14, 2], pad.r[15, 2], pad.r[7, 2]]

    temp_x = x1 + x2 + x3
    temp_y = y1 + y2 + y3
    temp_z = z1 + z2 + z3

    wf_pad = go.Scatter3d(x=temp_x, y=temp_y, z=temp_z, mode="lines",
                          hoverinfo="skip", visible=visible,
                          line=dict(color=wf_pad_color, width=line_width))

    # The following section creates a wireframe plot for the X-ray detector
    x1 = beam.det_r[0:4, 0].tolist() + [beam.det_r[0, 0]]
    y1 = beam.det_r[0:4, 1].tolist() + [beam.det_r[0, 1]]
    z1 = beam.det_r[0:4, 2].tolist() + [beam.det_r[0, 2]]

    x2 = beam.det_r[4:8, 0].tolist() + [beam.det_r[4, 0]]
    y2 = beam.det_r[4:8, 1].tolist() + [beam.det_r[4, 1]]
    z2 = beam.det_r[4:8, 2].tolist() + [beam.det_r[4, 2]]

    x3 = [beam.det_r[4, 0], beam.det_r[5, 0], beam.det_r[1, 0], beam.det_r[2, 0], beam.det_r[6, 0], beam.det_r[7, 0], beam.det_r[3, 0]]
    y3 = [beam.det_r[4, 1], beam.det_r[5, 1], beam.det_r[1, 1], beam.det_r[2, 1], beam.det_r[6, 1], beam.det_r[7, 1], beam.det_r[3, 1]]
    z3 = [beam.det_r[4, 2], beam.det_r[5, 2], beam.det_r[1, 2], beam.det_r[2, 2], beam.det_r[6, 2], beam.det_r[7, 2], beam.det_r[3, 2]]

    temp_x = x1 + x2 + x3
    temp_y = y1 + y2 + y3
    temp_z = z1 + z2 + z3

    wf_detector = go.Scatter3d(x=temp_x, y=temp_y, z=temp_z, mode="lines",
                               hoverinfo="skip", visible=visible,
                               line=dict(color=wf_detector_color,
                                         width=line_width))

    return wf_beam, wf_table, wf_pad, wf_detector
